#!/usr/bin/env python3
"""Agent Father toolkit: scaffold, validate and package agents built to Agent Standard v1.

Usage:
  father.py scaffold <name> [--title TITLE] [--out DIR] [--spec FILE]
  father.py validate <agent-dir> [--json]
  father.py package  <agent-dir> [--out DIR] [--force]
  father.py package-team <team-dir> [--out DIR]
  father.py inventory <folder> [--json]

Standard library only, Python 3.8+.
"""
import argparse
import contextlib
import io
import datetime
import json
import py_compile
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "assets" / "templates"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
FILL_RE = re.compile(r"<!--\s*FATHER:FILL")
PLACEHOLDER_RE = re.compile(r"\{\{[a-z_]+\}\}")
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
PATH_RE = re.compile(r"`((?:references|assets|scripts|tests)/[^`\s]*)`")

REQUIRED_SECTIONS = ["Scope", "Language", "How to work", "Workflows", "Output",
                     "Red lines", "When to escalate", "Resources"]
BASELINE_PHRASES = ["never invent", "data, not instructions", "explicit confirmation", "requires approval"]
MANIFEST_KEYS = ["name", "title", "version", "standard", "language", "archetypes",
                 "level", "autonomy", "changelog"]
NEVER_ALLOWLIST = re.compile(r"\b(pay|payment|transfer|refund|delete|deletion|erase|sign|signature|submit|"
                             r"grant|permission|price|contract|personal data)\w*", re.I)
OUTBOUND = re.compile(r"\b(send|email|e-mail|post|publish|message|reply)\w*", re.I)
SKILL_PARTS = ["SKILL.md", "references", "assets", "scripts"]
TEXT_EXT = {".md", ".yaml", ".yml", ".txt", ".csv", ".py", ".json"}
JUNK = {".DS_Store", "__pycache__", "Thumbs.db"}
SKILL_LINES_WARN = 250
SKILL_LINES_MAX = 500


# ---------- small parsers (no PyYAML dependency) ----------

def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def strip_comment(value):
    value = value.strip()
    if value and value[0] in "\"'":
        end = value.find(value[0], 1)
        return value[: end + 1] if end > 0 else value
    return value.split(" #", 1)[0].rstrip()


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None, text


def parse_frontmatter(lines):
    data, raw = {}, {}
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        raw[key] = val
        if val in ("", ">", "|", ">-", "|-"):
            block = []
            i += 1
            while i < len(lines) and (lines[i][:1] in (" ", "\t") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            if val == "":
                nested = {}
                for b in block:
                    mm = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", b)
                    if mm:
                        nested[mm.group(1)] = unquote(strip_comment(mm.group(2)))
                data[key] = nested
            else:
                data[key] = (" " if val.startswith(">") else "\n").join(block).strip()
            continue
        data[key] = unquote(val)
        i += 1
    return data, raw


def top_level_keys(text):
    keys = {}
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            keys[m.group(1)] = unquote(strip_comment(m.group(2)))
    return keys


def yaml_block(text, key):
    """Raw text of a top-level YAML key's block (value line + indented lines)."""
    m = re.search(r"^%s:(.*(?:\n(?:[ \t]+.*|[ \t]*))*)" % re.escape(key), text, re.M)
    return m.group(1) if m else ""


def list_items(block):
    """Split a YAML list block into item texts ('- ...' entries with their indented lines)."""
    inline = block.strip()
    if inline.startswith("["):
        return [x.strip() for x in inline.strip("[]").split(",") if x.strip()]
    return [i.strip() for i in re.split(r"\n[ \t]*-[ \t]", "\n" + block) if i.strip()]


def iter_files(root):
    for p in sorted(root.rglob("*")):
        if p.is_file() and not any(part in JUNK for part in p.parts):
            yield p


def rel(path, root):
    return path.relative_to(root).as_posix()


# ---------- validate ----------

class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def check_paths(text, source, agent, rep, strict):
    """Check that referenced package paths exist. strict=True -> errors, else warnings."""
    found = set(PATH_RE.findall(text))
    for link in MD_LINK_RE.findall(text):
        if not re.match(r"^(https?:|mailto:|#)", link):
            found.add(link.split("#", 1)[0])
    for ref in sorted(found):
        if not ref or any(c in ref for c in "<>*{}"):
            continue
        if not strict and "." not in ref.rsplit("/", 1)[-1]:
            continue  # directory mention inside a reference doc: descriptive, skip
        candidates = [agent / ref, (agent / source).parent / ref]
        if not any(c.exists() for c in candidates):
            (rep.error if strict else rep.warn)("%s: referenced path not found: %s" % (source, ref))


def validate(agent):
    rep = Report()
    agent = agent.resolve()
    folder = agent.name

    if not NAME_RE.match(folder) or len(folder) > 64:
        rep.error("folder name '%s' must be lowercase-hyphen, max 64 chars" % folder)

    for required in ["SKILL.md", "manifest.yaml", "spec.yaml", "README.md", "tests/cases.yaml"]:
        if not (agent / required).is_file():
            rep.error("missing file: %s" % required)

    # manifest
    manifest = {}
    if (agent / "manifest.yaml").is_file():
        mtext = (agent / "manifest.yaml").read_text(encoding="utf-8")
        manifest = top_level_keys(mtext)
        for key in MANIFEST_KEYS:
            if key not in manifest:
                rep.error("manifest.yaml: missing key '%s'" % key)
        if manifest.get("name") and manifest["name"] != folder:
            rep.error("manifest.yaml: name '%s' != folder '%s'" % (manifest["name"], folder))
        version = manifest.get("version", "")
        if version and not SEMVER_RE.match(version):
            rep.error("manifest.yaml: version '%s' is not X.Y.Z" % version)
        if manifest.get("level") and manifest["level"] not in ("L1", "L2", "L3"):
            rep.error("manifest.yaml: level must be L1, L2 or L3")
        if version and not re.search(r"version:\s*[\"']?%s[\"']?\s*$" % re.escape(version),
                                     mtext.split("changelog:", 1)[-1], re.M):
            rep.warn("manifest.yaml: no changelog entry for version %s" % version)
        has_connectors = bool(re.search(r"^connectors:[ \t]*\n[ \t]+-\s", mtext, re.M) or
                              re.search(r"^connectors:[ \t]*\[[ \t]*[^\]\s]", mtext, re.M))
        if has_connectors and manifest.get("level") != "L3":
            rep.error("manifest.yaml: connectors declared but level is not L3")
        if manifest.get("level") == "L3" and not has_connectors:
            rep.warn("manifest.yaml: level L3 but no connectors declared")
        if has_connectors:
            block = mtext.split("connectors:", 1)[1].split("changelog:", 1)[0]
            if "capability:" not in block or "access:" not in block:
                rep.error("manifest.yaml: each connector needs 'capability' and 'access' (standard §8a)")

        # autonomy, memory, schedules (standard 8b-8d)
        autonomy = manifest.get("autonomy", "")
        if autonomy and autonomy not in ("0", "1", "2", "3"):
            rep.error("manifest.yaml: autonomy must be 0, 1, 2 or 3")
        actions = list_items(yaml_block(mtext, "allowed_actions"))
        if autonomy == "3":
            if not actions:
                rep.error("manifest.yaml: autonomy 3 needs allowed_actions (standard 8b)")
            for item in actions:
                for field in ("action", "capability", "limits"):
                    if field + ":" not in item:
                        rep.error("manifest.yaml: allowed action needs '%s': %s" % (field, item.splitlines()[0]))
                bad = NEVER_ALLOWLIST.search(item)
                if bad:
                    rep.error("manifest.yaml: '%s' can never be allowlisted (standard 8b): %s"
                              % (bad.group(0), item.splitlines()[0]))
                elif OUTBOUND.search(item) and not re.search(r"internal|draft", item, re.I):
                    rep.error("manifest.yaml: outbound action allowlisted without 'internal' or 'draft' "
                              "scope (standard 8b): %s" % item.splitlines()[0])
        elif actions:
            rep.warn("manifest.yaml: allowed_actions are ignored below autonomy 3")
        has_scripts = (agent / "scripts").is_dir() and any((agent / "scripts").rglob("*.py"))
        if autonomy in ("2", "3") and not has_connectors and not has_scripts:
            rep.warn("manifest.yaml: autonomy %s but no connectors — the agent has no system to act on "
                     "and effectively works at level 1; add connectors or lower autonomy" % autonomy)
        schedules = list_items(yaml_block(mtext, "schedules"))
        if schedules and autonomy != "3":
            rep.warn("manifest.yaml: scheduled runs below autonomy 3 can only report, not act")
    ignore_markers = [p.strip().strip("/") for p in
                      manifest.get("ignore_markers_in", "").strip("[]").split(",") if p.strip()]

    # SKILL.md
    skill_text, body = "", ""
    if (agent / "SKILL.md").is_file():
        skill_text = (agent / "SKILL.md").read_text(encoding="utf-8")
        fm_lines, body = split_frontmatter(skill_text)
        if fm_lines is None:
            rep.error("SKILL.md: missing YAML frontmatter (--- ... ---)")
            fm, raw = {}, {}
        else:
            fm, raw = parse_frontmatter(fm_lines)
        name = fm.get("name", "")
        if name != folder:
            rep.error("SKILL.md: name '%s' != folder '%s'" % (name, folder))
        desc = fm.get("description", "")
        if not desc:
            rep.error("SKILL.md: description is empty")
        else:
            if len(desc) > 1024:
                rep.error("SKILL.md: description is %d chars (max 1024)" % len(desc))
            if "use when" not in desc.lower():
                rep.warn("SKILL.md: description has no 'Use when ...' trigger clause")
            rd = raw.get("description", "")
            if rd and rd[:1] not in "\"'>|" and (": " in rd or " #" in rd):
                rep.error("SKILL.md: description contains ': ' or ' #' unquoted — wrap it in quotes "
                          "or use 'description: >' so YAML parsers accept it")
        meta_version = fm.get("metadata", {}).get("version") if isinstance(fm.get("metadata"), dict) else None
        if manifest.get("version") and meta_version != manifest.get("version"):
            rep.error("SKILL.md: metadata.version '%s' != manifest version '%s'"
                      % (meta_version, manifest.get("version")))

        n_lines = len(skill_text.splitlines())
        if n_lines > SKILL_LINES_MAX:
            rep.error("SKILL.md: %d lines (max %d) — move detail to references/" % (n_lines, SKILL_LINES_MAX))
        elif n_lines > SKILL_LINES_WARN:
            rep.warn("SKILL.md: %d lines (target <= %d)" % (n_lines, SKILL_LINES_WARN))

        if not re.search(r"^# \S", body, re.M):
            rep.error("SKILL.md: missing '# Title' heading")
        headings = {h.strip().lower() for h in re.findall(r"^##\s+(.+)$", body, re.M)}
        for section in REQUIRED_SECTIONS:
            if section.lower() not in headings:
                rep.error("SKILL.md: missing section '## %s'" % section)
        red = re.search(r"^## Red lines\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
        red_text = red.group(1).lower() if red else ""
        for phrase in BASELINE_PHRASES:
            if phrase not in red_text:
                rep.error("SKILL.md: Red lines lack the baseline rule containing '%s'" % phrase)

        check_paths(skill_text, "SKILL.md", agent, rep, strict=True)

    mtext_all = (agent / "manifest.yaml").read_text(encoding="utf-8") if (agent / "manifest.yaml").is_file() else ""
    if skill_text:
        if manifest.get("autonomy") == "3" and not re.search(r"^## Autonomy\s*$", body, re.M):
            rep.error("SKILL.md: autonomy 3 requires a '## Autonomy' section")
        if manifest.get("memory") == "true" and not re.search(r"^## Memory\s*$", body, re.M):
            rep.error("SKILL.md: memory true requires a '## Memory' section")
    sched = list_items(yaml_block(mtext_all, "schedules"))
    if sched:
        readme = (agent / "README.md").read_text(encoding="utf-8") if (agent / "README.md").is_file() else ""
        if "## Scheduled tasks" not in readme:
            rep.error("README.md: schedules declared but no '## Scheduled tasks' section")
        for it in sched:
            m = re.search(r"workflow:\s*(\S+)", it)
            if not m:
                rep.error("manifest.yaml: schedule without workflow: %s" % it.splitlines()[0])
                continue
            wf = agent / "references" / "workflows" / (m.group(1) + ".md")
            if not wf.is_file():
                rep.error("manifest.yaml: scheduled workflow not found: %s" % rel(wf, agent))
            elif "## Scheduled run" not in wf.read_text(encoding="utf-8"):
                rep.error("%s: scheduled workflow needs a '## Scheduled run' section" % rel(wf, agent))

    # coverage: every workflow / knowledge / asset file is mentioned in SKILL.md
    for sub in ["references/workflows", "references/knowledge", "assets"]:
        base = agent / sub
        if not base.is_dir():
            continue
        for f in iter_files(base):
            r = rel(f, agent)
            parents = [rel(p, agent) + "/" for p in f.parents if p != agent and agent in p.parents]
            if not any(token in skill_text for token in [r, f.name] + parents):
                rep.warn("%s is not mentioned in SKILL.md" % r)

    # reference docs: broken links, leftovers
    for f in iter_files(agent):
        r = rel(f, agent)
        if f.suffix.lower() not in TEXT_EXT:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        skip_markers = f.suffix == ".py" or any(r == p or r.startswith(p + "/") for p in ignore_markers)
        if not skip_markers and FILL_RE.search(text):
            rep.error("%s: unfilled FATHER:FILL marker" % r)
        if not skip_markers and not r.startswith("assets/") and PLACEHOLDER_RE.search(text):
            rep.error("%s: unfilled {{placeholder}}" % r)
        if r.startswith("references/") and f.suffix == ".md":
            check_paths(text, r, agent, rep, strict=False)
        if r.startswith("references/knowledge/") and "TODO: verify" in text:
            rep.warn("%s: %d 'TODO: verify' items — tell the user what to fill"
                     % (r, text.count("TODO: verify")))

    # tests
    cases_file = agent / "tests" / "cases.yaml"
    if cases_file.is_file():
        ctext = cases_file.read_text(encoding="utf-8")
        ids = re.findall(r"^\s*-\s+id:\s*(\S+)", ctext, re.M)
        types = re.findall(r"^\s+type:\s*([a-z-]+)", ctext, re.M)
        if len(ids) < 5:
            rep.error("tests/cases.yaml: %d cases (min 5)" % len(ids))
        if len(set(ids)) != len(ids):
            rep.error("tests/cases.yaml: duplicate case ids")
        if types.count("core") < 3:
            rep.error("tests/cases.yaml: %d core cases (min 3)" % types.count("core"))
        for t in ("edge", "red-line"):
            if t not in types:
                rep.error("tests/cases.yaml: no '%s' case" % t)
        for line in re.findall(r"^\s+inputs:\s*\[(.*)\]\s*$", ctext, re.M):
            for item in [unquote(x) for x in line.split(",") if x.strip()]:
                if not (agent / item).exists():
                    rep.error("tests/cases.yaml: input not found: %s" % item)

    # README
    if (agent / "README.md").is_file():
        rtext = (agent / "README.md").read_text(encoding="utf-8")
        if len(re.findall(r"^## ", rtext, re.M)) < 3:
            rep.warn("README.md: fewer than 3 sections")
        if manifest.get("version") and manifest["version"] not in rtext:
            rep.warn("README.md: does not mention current version %s" % manifest["version"])

    # scripts
    scripts = [p for p in (agent / "scripts").rglob("*.py")] if (agent / "scripts").is_dir() else []
    for s in scripts:
        if any(part in JUNK for part in s.parts):
            continue
        try:
            with tempfile.TemporaryDirectory() as tmp:
                py_compile.compile(str(s), cfile=str(Path(tmp) / "x.pyc"), doraise=True)
        except py_compile.PyCompileError as exc:
            rep.error("%s: does not compile: %s" % (rel(s, agent), exc.msg.strip().splitlines()[-1]))
    if scripts and manifest.get("level") == "L1":
        rep.warn("scripts/ present but manifest level is L1 — set L2 or explain")

    return rep


def cmd_validate(args):
    agent = Path(args.agent_dir)
    if not agent.is_dir():
        print("not a directory: %s" % agent, file=sys.stderr)
        return 2
    rep = validate(agent)
    status = "error" if rep.errors else ("warning" if rep.warnings else "ok")
    if args.json:
        print(json.dumps({"status": status, "errors": rep.errors, "warnings": rep.warnings,
                          "summary": "%d errors, %d warnings" % (len(rep.errors), len(rep.warnings))},
                         ensure_ascii=False, indent=2))
    else:
        for e in rep.errors:
            print("ERROR  " + e)
        for w in rep.warnings:
            print("WARN   " + w)
        print("%s: %s — %d errors, %d warnings" % (agent.resolve().name, status.upper(),
                                                   len(rep.errors), len(rep.warnings)))
    return 1 if rep.errors else 0


# ---------- scaffold ----------

def render(template, values):
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    for k, v in values.items():
        text = text.replace("{{%s}}" % k, v)
    return text


def cmd_scaffold(args):
    name = args.name
    if not NAME_RE.match(name) or len(name) > 64:
        print("name must be lowercase-hyphen, max 64 chars: %s" % name, file=sys.stderr)
        return 2
    target = Path(args.out) / name
    if target.exists():
        print("already exists: %s" % target, file=sys.stderr)
        return 2
    values = {"name": name, "title": args.title or name, "version": "0.1.0",
              "date": datetime.date.today().isoformat()}
    files = {
        "SKILL.md": "SKILL.template.md",
        "tests/cases.yaml": "cases.yaml",
        "manifest.yaml": "manifest.yaml",
        "README.md": "README.md",
    }
    for dest, tmpl in files.items():
        path = target / dest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(tmpl, values), encoding="utf-8")
    for d in ["references/workflows", "references/knowledge", "assets", "tests/fixtures"]:
        (target / d).mkdir(parents=True, exist_ok=True)
    spec_src = Path(args.spec) if args.spec else TEMPLATES / "spec.yaml"
    spec_text = spec_src.read_text(encoding="utf-8")
    if not args.spec:
        spec_text = spec_text.replace("<domain-role>", name, 1)
    (target / "spec.yaml").write_text(spec_text, encoding="utf-8")
    print(json.dumps({"status": "ok", "summary": "scaffolded %s" % target,
                      "artifacts": [rel(p, target.parent) for p in iter_files(target)],
                      "next_actions": ["fill files in the order of create-agent.md step 6",
                                       "create workflow and knowledge files from assets/templates/",
                                       "run: father.py validate %s" % target]},
                     ensure_ascii=False, indent=2))
    return 0


# ---------- package ----------

def flat_name(ref_path):
    """references/workflows/a.md -> workflows--a.md ; assets/x/y.docx -> x--y.docx"""
    parts = ref_path.split("/")[1:]
    return "--".join(parts)


def portable_rewrite(text):
    text = re.sub(r"^All paths below are relative to this skill's folder\..*\n+", "", text, flags=re.M)
    return re.sub(r"\b((?:references|assets)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)",
                  lambda m: flat_name(m.group(1)), text)


def copy_tree(src, dst):
    for f in iter_files(src):
        out = dst / f.relative_to(src)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)


def zip_dir(src_dir, zip_path, arc_root):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in iter_files(src_dir):
            z.write(f, (Path(arc_root) / f.relative_to(src_dir)).as_posix())


def cmd_package(args):
    agent = Path(args.agent_dir).resolve()
    rep = validate(agent)
    if rep.errors and not args.force:
        for e in rep.errors:
            print("ERROR  " + e, file=sys.stderr)
        print("validation failed — fix errors or use --force", file=sys.stderr)
        return 1
    manifest = top_level_keys((agent / "manifest.yaml").read_text(encoding="utf-8"))
    name, version = agent.name, manifest.get("version", "0.0.0")
    title = manifest.get("title", name)
    if args.out:
        out = Path(args.out).resolve()
    elif agent.parent.name == "agents":
        out = agent.parent.parent / "dist"
    else:
        out = agent.parent / "dist"
    dest = out / ("%s-%s" % (name, version))
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    # 1. skill folder + skill zip
    skill_dir = dest / name
    for part in SKILL_PARTS:
        src = agent / part
        if src.is_file():
            skill_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, skill_dir / part)
        elif src.is_dir():
            copy_tree(src, skill_dir / part)
    zip_dir(skill_dir, dest / ("%s.zip" % name), name)

    # 2. portable export
    portable = dest / "portable"
    (portable / "knowledge").mkdir(parents=True)
    notes = []
    seen = {}
    for f in iter_files(agent / "references") if (agent / "references").is_dir() else []:
        r = rel(f, agent)
        target = portable / "knowledge" / flat_name(r)
        if target.name in seen:
            notes.append("name collision: %s and %s" % (seen[target.name], r))
        seen[target.name] = r
        if f.suffix == ".md":
            target.write_text(portable_rewrite(f.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(f, target)
    if (agent / "assets").is_dir():
        for f in iter_files(agent / "assets"):
            target = portable / "assets" / flat_name(rel(f, agent))
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
    _, body = split_frontmatter((agent / "SKILL.md").read_text(encoding="utf-8"))
    header = (
        "> Portable version of %s v%s for chat tools without Agent Skills support.\n"
        "> Files are attached to this project with flattened names: `references/workflows/x.md` "
        "is `workflows--x.md`, `assets/a/b.docx` is `a--b.docx`. A folder mentioned in the text "
        "means all attached files whose names start with it.\n"
        "> If only ALL-IN-ONE.md is attached, find each file there under its 'FILE:' heading.\n"
        "> Scripts cannot run here: follow the 'Without scripts' section of each workflow.\n\n"
        % (name, version))
    instructions = header + portable_rewrite(body.lstrip())
    (portable / "INSTRUCTIONS.md").write_text(instructions, encoding="utf-8")
    # one combined file for tools that prefer few uploads (Gemini Gems, ChatGPT projects)
    parts = ["# %s v%s — all knowledge and templates\n\nEach section below is one file; its name is the heading.\n"
             % (title, version)]
    for sub in ("knowledge", "assets"):
        base = portable / sub
        if base.is_dir():
            for f in sorted(base.iterdir()):
                if f.is_file() and f.suffix.lower() in TEXT_EXT:
                    parts.append("\n\n---\n\n## FILE: %s\n\n%s" % (f.name, f.read_text(encoding="utf-8")))
    (portable / "ALL-IN-ONE.md").write_text("".join(parts), encoding="utf-8")

    # 3. human docs, tests, records
    for doc in ["README.md", "manifest.yaml", "spec.yaml"]:
        if (agent / doc).is_file():
            shutil.copy2(agent / doc, dest / doc)
    if (agent / "tests").is_dir():
        copy_tree(agent / "tests", dest / "tests")

    # 4. full bundle
    bundle = out / ("%s-%s.zip" % (name, version))
    zip_dir(dest, bundle, dest.name)

    print(json.dumps({
        "status": "warning" if (rep.errors or rep.warnings or notes) else "ok",
        "summary": "packaged %s v%s (%s)" % (name, version, title),
        "artifacts": [str(bundle), str(dest / ("%s.zip" % name)), str(portable / "INSTRUCTIONS.md")],
        "warnings": rep.warnings + notes + (["packaged with errors (--force)"] if rep.errors else []),
        "next_actions": ["hand %s to the user" % bundle.name,
                         "point them to README.md -> installation for their platform"],
    }, ensure_ascii=False, indent=2))
    return 0


# ---------- inventory ----------

def _docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", "", xml)


def _xlsx_sheets(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("xl/workbook.xml").decode("utf-8", "replace")
    return re.findall(r'<sheet[^>]*name="([^"]+)"', xml)


def cmd_inventory(args):
    root = Path(args.folder).resolve()
    if not root.is_dir():
        print("not a directory: %s" % root, file=sys.stderr)
        return 2
    items = []
    for f in iter_files(root):
        ext = f.suffix.lower()
        item = {"path": rel(f, root), "type": ext.lstrip(".") or "none",
                "size_kb": round(f.stat().st_size / 1024, 1), "readable": True, "preview": "", "words": None}
        try:
            if ext in (".txt", ".md", ".csv", ".tsv", ".json", ".yaml", ".yml", ".html", ".xml"):
                text = f.read_text(encoding="utf-8", errors="replace")
            elif ext == ".docx":
                text = _docx_text(f)
            elif ext in (".xlsx", ".xlsm"):
                text = None
                item["preview"] = "sheets: " + ", ".join(_xlsx_sheets(f))
            else:
                text = None
                item["readable"] = False
                item["preview"] = "use the platform's file tools (pdf, images, pptx, xls...)"
            if text is not None:
                item["words"] = len(text.split())
                item["preview"] = " ".join(text.split())[:200]
        except (zipfile.BadZipFile, KeyError, OSError) as exc:
            item["readable"] = False
            item["preview"] = "cannot read: %s" % exc
        items.append(item)
    summary = "%d files, %d readable here, %d need platform file tools" % (
        len(items), sum(i["readable"] for i in items), sum(not i["readable"] for i in items))
    if args.json:
        print(json.dumps({"status": "ok", "summary": summary, "files": items}, ensure_ascii=False, indent=2))
    else:
        for i in items:
            print("%-50s %-6s %8.1f KB  %s" % (i["path"][:50], i["type"], i["size_kb"], i["preview"][:80]))
        print(summary)
    return 0


# ---------- teams ----------

def parse_team(text):
    team = {"members": [], "shared": []}
    current = None
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), strip_comment(m.group(2))
            current = key if key in ("members", "shared") and not val else None
            if key in ("members", "shared") and val.startswith("["):
                team[key] = [unquote(x) for x in val.strip("[]").split(",") if x.strip()]
            elif key not in ("members", "shared"):
                team[key] = unquote(val)
            continue
        m = re.match(r"^\s+-\s*(.+)$", line)
        if m and current:
            team[current].append(unquote(strip_comment(m.group(1))))
    return team


def cmd_package_team(args):
    team_dir = Path(args.team_dir).resolve()
    tfile = team_dir / "team.yaml"
    if not tfile.is_file():
        print("missing %s" % tfile, file=sys.stderr)
        return 2
    team = parse_team(tfile.read_text(encoding="utf-8"))
    name, version = team.get("name", team_dir.name), team.get("version", "0.0.0")
    agents_dir = team_dir.parent.parent / "agents"
    roster = ([team["lead"]] if team.get("lead") else []) + team["members"]
    problems = []
    for agent in roster:
        adir = agents_dir / agent
        if not adir.is_dir():
            problems.append("member not found: %s" % adir)
            continue
        kdir = adir / "references" / "knowledge"
        kdir.mkdir(parents=True, exist_ok=True)
        for shared in team["shared"]:
            src = team_dir / "shared" / shared
            if not src.is_file():
                problems.append("shared file not found: %s" % src)
                continue
            shutil.copy2(src, kdir / ("shared-" + Path(shared).name))
        rep = validate(adir)
        problems += ["%s: %s" % (agent, e) for e in rep.errors]
    if problems:
        for pr in problems:
            print("ERROR  " + pr, file=sys.stderr)
        print("team validation failed", file=sys.stderr)
        return 1
    out = Path(args.out).resolve() if args.out else team_dir.parent.parent / "dist"
    dest = out / ("%s-%s" % (name, version))
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for agent in roster:
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_package(argparse.Namespace(agent_dir=str(agents_dir / agent), out=str(dest), force=False))
        for z in dest.glob("%s-*.zip" % agent):
            z.unlink()  # keep unpacked member folders inside the team bundle only
    for doc in ["README.md", "team.yaml"]:
        if (team_dir / doc).is_file():
            shutil.copy2(team_dir / doc, dest / doc)
    bundle = out / ("%s-%s.zip" % (name, version))
    zip_dir(dest, bundle, dest.name)
    print(json.dumps({"status": "ok", "summary": "packaged team %s v%s: %s" % (name, version, ", ".join(roster)),
                      "artifacts": [str(bundle)],
                      "next_actions": ["hand %s to the user" % bundle.name,
                                       "install every member and the lead together (team README)"]},
                     ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="father.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("scaffold", help="create an agent skeleton from templates")
    s.add_argument("name")
    s.add_argument("--title")
    s.add_argument("--out", default=".")
    s.add_argument("--spec", help="approved spec.yaml to copy into the agent")
    v = sub.add_parser("validate", help="check an agent against the standard")
    v.add_argument("agent_dir")
    v.add_argument("--json", action="store_true")
    k = sub.add_parser("package", help="build distributable zips and the portable export")
    k.add_argument("agent_dir")
    k.add_argument("--out")
    k.add_argument("--force", action="store_true")
    t = sub.add_parser("package-team", help="validate and package a team of agents")
    t.add_argument("team_dir")
    t.add_argument("--out")
    i = sub.add_parser("inventory", help="list a folder of source documents")
    i.add_argument("folder")
    i.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "scaffold":
        return cmd_scaffold(args)
    if args.cmd == "validate":
        return cmd_validate(args)
    if args.cmd == "package":
        return cmd_package(args)
    if args.cmd == "package-team":
        return cmd_package_team(args)
    if args.cmd == "inventory":
        return cmd_inventory(args)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
