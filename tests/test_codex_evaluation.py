import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from evals.codex.graders.runtime import classify_runtime, selected_skill
from scripts.run_codex_evaluation import (
    deterministic_checks,
    calibration_status,
    live_probe,
    marker_command,
    parse_runtime_events,
    routing_command,
    serialize_routing_result,
    auth_status_command,
    eval_home_path,
    instrumented_prompt,
    marketplace_add_command,
    plugin_install_command,
    plugin_is_exposed,
    plugin_list_command,
    stage_local_marketplace,
    stage_skill_text,
)


class CodexEvaluationTests(unittest.TestCase):
    def test_deterministic_cases_pass(self):
        self.assertTrue(all(case["status"] == "PASS" for case in deterministic_checks()))

    def test_selection_requires_runtime_evidence(self):
        self.assertEqual(selected_skill([{"type": "agent_message", "text": "I used testing-qa"}]), "UNKNOWN")
        self.assertEqual(selected_skill([{"type": "skill_loaded", "name": "testing-qa"}]), "testing-qa")

    def test_result_classification(self):
        self.assertEqual(classify_runtime([]), "UNAVAILABLE")
        self.assertEqual(classify_runtime([{"type": "turn.completed"}]), "PASS")
        self.assertEqual(classify_runtime([{"type": "error"}]), "FAIL")

    def test_authored_fixture_locations_and_results_ignore(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "evals/codex/tasks/runtime-cases.json").is_file())
        self.assertTrue((root / "evals/codex/expected_invariants/runtime.json").is_file())
        self.assertIn("evals/codex/results/*", (root / ".gitignore").read_text(encoding="utf-8"))

    def test_routing_command_is_ephemeral_read_only_and_does_not_include_prompt(self):
        command = routing_command("codex")
        self.assertIn("--ephemeral", command)
        self.assertNotIn("--ignore-user-config", command)
        self.assertNotIn("--ask-for-approval", command)
        self.assertIn("read-only", command)
        self.assertEqual(command[-1], str(Path(__file__).resolve().parents[1]))

    def test_setup_commands_use_marketplace_root_and_explicit_install(self):
        root = Path("C:/eval/marketplace")
        self.assertEqual(marketplace_add_command("codex", root)[-1], str(root))
        self.assertEqual(plugin_install_command("codex", "codex-skills-eval")[-1], "codex-skills@codex-skills-eval")
        self.assertEqual(auth_status_command("codex")[1:], ["login", "status"])
        self.assertEqual(plugin_list_command("codex")[-1], "--json")

    def test_local_marketplace_stages_current_plugin_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = stage_local_marketplace(Path(directory))
            marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
            source = marketplace["plugins"][0]["source"]
            self.assertEqual(source, {"source": "local", "path": "./plugins/codex-skills"})
            self.assertTrue((root / source["path"][2:] / ".codex-plugin/plugin.json").is_file())
            self.assertTrue((root / source["path"][2:] / "skills").is_dir())

    def test_stage_instruments_body_without_changing_frontmatter(self):
        original = "---\nname: testing-qa\ndescription: Test skill\n---\n\nDo the thing.\n"
        staged = stage_skill_text(original, "testing-qa", "abcdef0123456789")
        self.assertEqual(staged.split("---", 2)[:2], original.split("---", 2)[:2])
        self.assertIn(marker_command("testing-qa", "abcdef0123456789"), staged)

    def test_marker_command_requires_exact_nonce_and_skill(self):
        command = marker_command("testing-qa", "abcdef0123456789")
        self.assertIn("abcdef0123456789", command)
        self.assertIn("testing-qa", command)
        self.assertNotEqual(command, marker_command("testing-qa", "abcdef0123456788"))

    def test_parser_accepts_only_command_execution_marker(self):
        command = marker_command("testing-qa", "abcdef0123456789")
        output = json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": command}})
        self.assertEqual(parse_runtime_events(output, command), [{"type": "skill_selected", "name": "testing-qa", "source": "injected-skill-marker-v1"}])
        prose = json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": command}})
        self.assertEqual(parse_runtime_events(prose, command), [])

    def test_calibration_distinguishes_success_and_missing_marker(self):
        self.assertEqual(calibration_status([{"type": "turn.completed"}], []), "INSTRUMENTATION_UNAVAILABLE")
        self.assertEqual(calibration_status([{"type": "turn.completed"}], [{"type": "skill_selected", "name": "testing-qa"}]), "ROUTING_AVAILABLE")
        self.assertEqual(calibration_status([{"type": "error"}], []), "RUNTIME_FAILURE")

    def test_dedicated_eval_home_is_required_before_provisioning(self):
        with patch("scripts.run_codex_evaluation.codex_version", return_value="codex 1"), patch.dict("os.environ", {}, clear=True):
            result = live_probe("codex")
        self.assertEqual(result["setup_failure"], "authentication")
        self.assertIn("CODEX_EVAL_HOME", result["reason"])

    def test_plugin_exposure_accepts_nested_json_listing(self):
        self.assertTrue(plugin_is_exposed({"installed": [{"name": "codex-skills", "installed": True, "enabled": True}]}))
        self.assertFalse(plugin_is_exposed({"installed": [{"name": "codex-skills", "installed": False}]}))
        self.assertFalse(plugin_is_exposed({"plugins": [{"name": "other"}]}))

    def test_setup_failures_are_classified_and_keep_cli_details(self):
        stages = [
            ("marketplace_registration", "marketplace add failed"),
            ("plugin_installation", "plugin add failed"),
            ("plugin_exposure", "plugin list failed"),
        ]
        for expected_stage, detail in stages:
            def run(command, **_kwargs):
                if command[1:3] == ["login", "status"]:
                    return subprocess.CompletedProcess(command, 0, "Logged in", "")
                if command[1:4] == ["plugin", "marketplace", "add"]:
                    return subprocess.CompletedProcess(command, 1 if expected_stage == "marketplace_registration" else 0, "", detail)
                if command[1:3] == ["plugin", "add"]:
                    return subprocess.CompletedProcess(command, 1 if expected_stage == "plugin_installation" else 0, "", detail)
                return subprocess.CompletedProcess(command, 1 if expected_stage == "plugin_exposure" else 0, "", detail)

            with self.subTest(stage=expected_stage), tempfile.TemporaryDirectory() as home, patch("scripts.run_codex_evaluation.codex_version", return_value="codex 1"), patch("scripts.run_codex_evaluation.git_commit", return_value="abc"), patch("scripts.run_codex_evaluation.subprocess.run", side_effect=run):
                result = live_probe("codex", codex_home=home, limit=1)
            self.assertEqual(result["setup_failure"], expected_stage)
            self.assertIn(detail, result["reason"])

    def test_event_parser_keeps_only_structured_grading_telemetry(self):
        command = marker_command("test-driven-development", "abcdef0123456789")
        events = parse_runtime_events('\n'.join([
            '{"type":"skill_loaded","name":"testing-qa","text":"private response"}',
            json.dumps({"type":"item.completed","item":{"type":"command_execution","command":command}}),
            '{"type":"turn.completed","text":"response body"}',
            'not json',
        ]), command)
        self.assertEqual(events, [{"type": "skill_loaded", "name": "testing-qa"}, {"type": "skill_selected", "name": "test-driven-development", "source": "injected-skill-marker-v1"}, {"type": "turn.completed"}])

    def test_instrumented_prompt_keeps_original_prompt(self):
        prompt = "Choose a skill."
        instrumented = instrumented_prompt(prompt)
        self.assertEqual(instrumented, prompt)

    def test_unavailable_without_installed_runtime(self):
        self.assertEqual(live_probe("codex-executable-that-does-not-exist")["status"], "RUNTIME_FAILURE")

    def test_result_serialization_is_metadata_only(self):
        case = {"case_id": "case-1", "prompt": "private prompt"}
        grading = {
            "expected_primary_skill": "testing-qa",
            "actual_selected_skills": [],
            "primary_selection_verdict": "UNKNOWN",
            "forbidden_activation_verdict": "NOT_APPLICABLE",
            "acceptable_alternative_handling": "NOT_USED",
            "expected_composition_sequence_verdict": "NOT_SPECIFIED",
            "routing_verdict": "UNKNOWN",
            "runtime_health": "PASS",
            "reason_codes": ["selection_evidence_unavailable"],
        }
        result = serialize_routing_result(case, grading, "codex 1")
        self.assertNotIn("prompt", result)
        self.assertEqual(result["implicit_routing_status"], "UNAVAILABLE")
        self.assertEqual(result["codex_version"], "codex 1")

    def test_case_filtering_is_deterministic_and_bounded(self):
        from scripts.run_codex_evaluation import select_routing_cases

        cases = [
            {"case_id": "a", "group_id": "g1"},
            {"case_id": "b", "group_id": "g2"},
            {"case_id": "c", "group_id": "g1"},
        ]
        self.assertEqual([c["case_id"] for c in select_routing_cases(cases, group="g1", limit=1)], ["a"])


if __name__ == "__main__":
    unittest.main()
