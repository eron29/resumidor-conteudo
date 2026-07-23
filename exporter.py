import markdown as md_lib

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Arial, sans-serif; max-width: 800px;
         margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1a1a1a; }}
  h1, h2, h3 {{ color: #2c3e50; }}
  h1 {{ border-bottom: 2px solid #2c3e50; padding-bottom: 8px; }}
  .meta {{ color: #666; font-size: 0.9em; margin-bottom: 24px; }}
  blockquote {{ border-left: 4px solid #ddd; margin-left: 0; padding-left: 16px; color: #555; }}
  code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
  pre {{ background: #f4f4f4; padding: 12px; border-radius: 5px; overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; }}
  hr {{ margin: 40px 0; border: none; border-top: 1px solid #ddd; }}
  @media print {{ body {{ margin: 0; }} }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def summary_to_html_block(title: str, meta: str, content_md: str) -> str:
    body_html = md_lib.markdown(content_md, extensions=["tables", "fenced_code"])
    return f"<h1>{title}</h1><div class='meta'>{meta}</div>{body_html}"


def export_single(title: str, meta: str, content_md: str) -> str:
    block = summary_to_html_block(title, meta, content_md)
    return HTML_TEMPLATE.format(title=title, body=block)


def export_batch(summaries) -> str:
    blocks = []
    for s in summaries:
        meta = f"Pasta: {s['folder_name'] or '-'} • Fonte: {s['source_type']} • Criado em: {s['created_at']}"
        blocks.append(summary_to_html_block(s["title"], meta, s["content_md"]))
    body = "<hr>".join(blocks)
    return HTML_TEMPLATE.format(title="Resumos Exportados", body=body)
