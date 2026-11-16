from gooddesign_chrome import footer as shared_footer
from gooddesign_chrome import navigation as shared_navigation


def navigation(active='projects', content_id='workspace-content'):
    if content_id not in ('workspace-content', 'main'):
        raise ValueError('unsupported content target')
    return shared_navigation(active)


def footer():
    return shared_footer()
