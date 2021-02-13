import json


def actionMessage(action, username, servername, *args):
    card = [
            {
                'type': 'card',
                'theme': 'secondary',
                'size': 'lg',
                'modules': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'paragraph',
                            'cols': 3,
                            'fields': [
                                {
                                    'type': 'kmarkdown',
                                    'content': f'**行为**\n{action}'
                                },
                                {
                                    'type': 'kmarkdown',
                                    'content': f'**ID**\n{username}'
                                },
                                {
                                    'type': 'kmarkdown',
                                    'content': f'**服务器**\n{servername}'
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    if 0 < len(args) <= 49:
        for text in args:
            card[0]['modules'].append(
              {
                "type": "section",
                "text": {
                  "type": "kmarkdown",
                  "content": str(text)
                }
              }
            )
    return json.dumps(card)
