import os
from typing import Dict, Any, List, Optional
from jinja2 import Environment, PackageLoader


def _create_env() -> Environment:
    return Environment(
        loader=PackageLoader("github_stats", "templates"),
        autoescape=False,
    )


def render_svgs(
    stats: Dict[str, Any],
    output_dir: str = ".",
    themes: Optional[List[str]] = None,
) -> List[str]:
    """Renders all SVG templates with the provided statistics."""

    env = _create_env()
    template_specs = [
        ("card.svg", "github-stats"),
        ("languages.svg", "github-languages"),
        ("recent.svg", "github-recent"),
    ]

    theme_list = themes or ["dark", "light"]
    os.makedirs(output_dir, exist_ok=True)

    outputs: List[str] = []
    for theme in theme_list:
        for template_name, output_base in template_specs:
            template = env.get_template(template_name)
            svg_content = template.render(**stats, theme=theme)
            output_filename = f"{output_base}-{theme}.svg"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            outputs.append(output_path)

    return outputs


