__artifacts_v2__ = {
    "appleIntelligenceReport": {
        "name": "Apple Intelligence Report",
        "description": (
            "Parses Apple Intelligence Report JSON files. Extracts model requests "
            "and Private Cloud Compute (PCC) requests including timestamps, user "
            "triggers, source apps, prompts and responses. Supports iOS, iPadOS "
            "and macOS reports."
        ),
        "author": "@malwr4n6",
        "version": "1.1.1",
        "date": "2026-07-19",
        "requirements": "none",
        "category": "Apple Intelligence",
        "notes": (
            "Apple Intelligence Reports can be exported via Settings > Privacy & Security > "
            "Apple Intelligence Report on iOS 18.4+ / macOS 15.4+. "
            "Detects on-device (Model Request) vs Private Cloud Compute (PCC) requests."
        ),
        "paths": ('*/Apple_Intelligence_Report*.json',),
        "output_types": "all",
        "artifact_icon": "cpu"
    }
}

import json
import re
from datetime import datetime, timezone, timedelta

from scripts.ilapfuncs import artifact_processor

USE_CASE_TRIGGER_MAP = {
    "summarization": "Summarize",
    "synopsis": "Summarize",
    "text_summarizer": "Summarize",
    "textComposition.OpenEndedTone": "Compose",
    "textComposition.OpenEndedToneQueryResponseV2": "Compose",
    "writingTools.compose": "Compose",
    "textComposition.TakeawaysTransform": "Key Points",
    "takeaways_transform": "Key Points",
    "textComposition.BulletsTransform": "List",
    "bullets_transform": "List",
    "textComposition.TablesTransform": "Table",
    "tables_transform": "Table",
    "GenerativeAssistant.knowledge": "Knowledge",
    "GenerativeAssistant.knowledgeFallback": "Knowledge",
    "GenerativeAssistant.composition": "Compose",
    "GenerativeAssistant.visualIntelligenceCamera": "Visual Intelligence",
    "VisualGeneration.GenerativePlayground": "Image Generation",
    "memoryCreation": "Memory Creation",
    "photos_memories": "Memory Creation",
}

CLIENT_APP_MAP = {
    "com.apple.siri": "Siri",
    "com.apple.WritingToolsUIService": "Writing Tools",
    "com.apple.GenerativePlaygroundApp": "Image Playground",
    "com.apple.mobileslideshow": "Photos",
    "com.apple.mobilesafari": "Safari",
    "com.apple.mail": "Mail",
    "com.apple.mobilemail": "Mail",
    "com.apple.MobileSMS": "Messages",
    "com.apple.Notes": "Notes",
}


def _epoch_to_utc(ts):
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError, TypeError):
        return str(ts)


def _epoch_to_local(ts, tz_offset):
    try:
        local_tz = timezone(timedelta(minutes=tz_offset))
        return datetime.fromtimestamp(ts, tz=local_tz).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError, TypeError):
        return str(ts)


def _extract_user_trigger(use_case, prompt_text, model):
    uc = use_case or ""
    for key, trigger in USE_CASE_TRIGGER_MAP.items():
        if key in uc:
            return trigger
    if model:
        for key, trigger in USE_CASE_TRIGGER_MAP.items():
            if key in model:
                return trigger
    if prompt_text and "templateID:" in prompt_text:
        m = re.search(r'templateID:\s*"([^"]+)"', prompt_text)
        if m:
            for key, trigger in USE_CASE_TRIGGER_MAP.items():
                if key in m.group(1):
                    return trigger
    if "VisualGeneration" in uc:
        return "Image Generation"
    if "GenerativeAssistant" in uc:
        return "Assistant"
    return uc if uc else "Unknown"


def _extract_source_app(client_id, use_case):
    if client_id:
        for key, name in CLIENT_APP_MAP.items():
            if key in client_id:
                return name
        return client_id
    if use_case:
        if "safari" in use_case.lower():
            return "Safari"
        if "photo" in use_case.lower() or "memory" in use_case.lower():
            return "Photos"
    return ""


def _extract_from_template(text):
    vb = re.search(r'variableBindings:\s*\[(.+?)\],\s*locale:', text, re.DOTALL)
    if vb:
        pairs = re.findall(r'"(\w+)":\s*"((?:[^"\\]|\\.)*)"', vb.group(1))
        parts = {}
        for k, v in pairs:
            if v and v.strip():
                parts[k] = v.replace("\\n", " ").replace("<n>", " ").strip()
        for k in ["userPrompt", "prompt", "userContent", "doc", "freeformStoryPromptQuery"]:
            if k in parts and parts[k]:
                val = parts[k]
                return val[:200] + "..." if len(val) > 200 else val
    matches = re.findall(r'string:\s*"((?:[^"\\]|\\.){10,})"', text)
    if matches:
        best = max(matches, key=len)
        return (best[:200] + "...").replace("<n>", " ") if len(best) > 200 else best.replace("<n>", " ")
    return "(template-based prompt)"


def _extract_request(prompt_text):
    if not prompt_text:
        return ""
    s = prompt_text.strip()
    if s == "<image>":
        return "<image input>"
    if s.startswith("PromptTemplateInfo("):
        return _extract_from_template(s)
    if s.startswith("{") and '"prompt"' in s:
        try:
            parts = s.split("<n>", 1)
            obj = json.loads(parts[0])
            base = obj.get("prompt", "")
            orig = obj.get("originalText", "")
            r = base
            if orig:
                r += f" [on: {orig[:80]}...]" if len(orig) > 80 else f" [on: {orig}]"
            if len(parts) > 1:
                r += f" >> {parts[1]}"
            return r
        except json.JSONDecodeError:
            pass
    return s.replace("<n>", " | ")


def _extract_response(response_text):
    if not response_text:
        return ""
    s = response_text.strip()
    if s == "<tool-call>":
        return "<tool action triggered>"
    if "<image>" in s:
        t = s.replace("<image>", "").strip()
        return t if t else "<image generated>"
    if s.startswith("<file>"):
        t = s.replace("<file>", "").strip()
        try:
            return json.loads(t).get("content", t)
        except json.JSONDecodeError:
            return t if t else "<file generated>"
    if s.startswith("{"):
        try:
            obj = json.loads(s)
            c = obj.get("content", "") or obj.get("body", "") or obj.get("summary", "")
            return c[:500] + "..." if len(c) > 500 else c
        except json.JSONDecodeError:
            pass
    return s[:500] + "..." if len(s) > 500 else s


@artifact_processor
def appleIntelligenceReport(files_found, report_folder, seeker, wrap_text, timezone_offset):
    """
    Parses Apple Intelligence Report JSON files.
    Author: Bhargav Rathod (@malwr4n6) - https://malwr4n6.com
    """
    data_list = []
    source_path = ""

    for file_found in files_found:
        source_path = str(file_found)

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        model_reqs = data.get("modelRequests", [])
        pcc_reqs = data.get("privateCloudComputeRequests", [])

        for e in model_reqs:
            ts = e.get("timestamp", 0)
            prompt = e.get("prompt", "")
            use_case = e.get("useCase", "")
            model = e.get("model", "")

            data_list.append((
                _epoch_to_utc(ts),
                _epoch_to_local(ts, timezone_offset),
                e.get("identifier", ""),
                _extract_user_trigger(use_case, prompt, model),
                use_case,
                _extract_source_app(e.get("clientIdentifier", ""), use_case),
                _extract_request(prompt),
                _extract_response(e.get("response", "")),
                model,
                "Model Request",
            ))

        for e in pcc_reqs:
            ts = e.get("timestamp", 0)
            pipeline = e.get("pipelineKind", "")
            params = {}
            try:
                params = json.loads(e.get("pipelineParameters", "{}"))
            except (json.JSONDecodeError, TypeError):
                pass

            adapter = params.get("adapter", "")
            model = params.get("model", "")
            nodes = e.get("nodes", [])
            validated = sum(1 for n in nodes if n.get("nodeState") == "Validated")

            data_list.append((
                _epoch_to_utc(ts),
                _epoch_to_local(ts, timezone_offset),
                e.get("requestId", ""),
                _extract_user_trigger("", "", adapter),
                pipeline,
                f"PCC ({pipeline})",
                f"Pipeline: {pipeline}",
                f"Adapter: {adapter} | Model: {model} | Nodes: {len(nodes)} ({validated} validated)",
                model,
                "PCC Request",
            ))

    data_headers = (
        ("Timestamp (UTC)", "datetime"),
        "Timestamp (Local)",
        "Event ID",
        "User Trigger",
        "Use Case (Raw)",
        "Source App",
        "Request",
        "Response",
        "Model",
        "Type",
    )

    return data_headers, data_list, source_path
