#!/usr/bin/env bash
# PostToolUse (Edit|Write): per-plugin copy on the landing page has ONE source —
# the PLUGINS object in docs/index.html. The catalog cards and the plugin views
# both render from it. Remind where to edit so the rendered output isn't hand-patched.

fp=$(jq -r '.tool_input.file_path // empty' 2>/dev/null)
case "$fp" in
  */docs/index.html)
    echo 'docs/index.html: per-plugin gloss/what/commands come from the PLUGINS object — the catalog (#catalog) and plugin views render from it. Edit copy there, not the generated markup.'
    ;;
esac
exit 0
