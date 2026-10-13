# Chat mode

Use when you cannot create files (plain chat, some web interfaces). The flow is the same; only delivery changes.

## Delivery

1. After spec approval, list the files you will produce (paths from standard §1) and say you will send them one by one.
2. Send each file as:

   ### `accounting-assistant/references/workflows/reconcile.md`
   ```markdown
   ...file content...
   ```

   Use the fence language matching the file (`markdown`, `yaml`, `python`). Never put two files in one block.
3. Order: SKILL.md → workflows → knowledge → assets → tests → manifest → README. If the reply is cut off, continue from the last complete file when the user says "continue".
4. Skip the validator; go through `checklist.md` yourself and report the result in 3–5 lines.

## If code execution is available (e.g. a Python sandbox)

Write the files inside the sandbox, run `father.py validate` and `package` if you have the script, and give the user the zip to download.

## Telling the user how to save

Short instructions in their language:
- create a folder named after the agent,
- save each block as a file with the shown path,
- then follow the README "Installation" section for their platform.

For chat tools without skill support: paste the SKILL.md text (without the `---` header) into the project or custom assistant instructions, and upload the `references/` files as knowledge files.
