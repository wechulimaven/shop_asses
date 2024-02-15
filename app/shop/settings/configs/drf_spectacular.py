SPECTACULAR_SETTINGS = {
    'TITLE': 'Hop Hub',
    'DESCRIPTION': 'Hop Hub API Documentation',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'SERVE_INCLUDE_SCHEMA': False,
    'URL_FORMAT_OVERRIDE': None,
    'PREPROCESSING_HOOKS': [
        'drf_spectacular.hooks.preprocess_exclude_path_format',
    ],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'filter': True,
        'displayRequestDuration': True,
        'syntaxHighlight.activate': True,
        'syntaxHighlight.theme': 'monokai',
    },
}