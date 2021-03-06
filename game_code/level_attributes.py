from sound_init import fir_level_music, sec_level_music, thi_level_music, for_level_music, fif_level_music

SCREENS = [
    {
        'title': 'Битва за Броды',
        'text': [' Во время наступления нацистской Германии на СССР в 1941 году на территории',
                 'западной Украины схлестнулись советские и немецкие танки.',
                 'Ваша цель:',
                 'уничтожить танки противника и защитить небольшую деревушку, чтобы ',
                 'обеспечить отступление остальных сил.'],
        'background': 'battle_for_fords.jpg',
    },

    {
        'title': 'Смоленское сражение',
        'text': [' После ожесточенных боев советские войска отступили к Смоленску.',
                 'Вам необходимо уничтожить группу фашистских танков,',
                 'чтобы замедлить дальнейшее наступление противника'],
        'background': 'battle_for_smolensk.jpg',
    },

    {
        'title': 'Битва за Москву',
        'text': [' Отступив к Москве, войска РККА дали масштабное сражение неприятелю',
                 'Вы должны уничтожить танки противника, чтобы остановить наступление захватчиков'],
        'background': 'battle_for_moscow.jpg',
    },

    {
        'title': 'Курская битва',
        'text': [' Прошло уже много битв, наступил решающей момент.',
                 'Это сражение должно стать переломным в войне!',
                 'Уничтожьте группу танков противника любой ценой,',
                 'и тогда вы поможете обеспечить контрнаступление советской армии.'],
        'background': 'battle_for_kursk.jpg',
    },

    {
        'title': 'Штурм Берлина',
        'text': [' Советские войска уже подошли к Берлину!',
                 'Вам нужно уничтожить несколько оставшихся танков противника,',
                 'аккуратно маневрируя между домами города'],
        'background': 'battle_for_berlin.jpg',
    },
]

LEVELS = [[(SCREENS[0]['title'], SCREENS[0]['text'], SCREENS[0]['background']),
           '1_level.txt'],
          [(SCREENS[1]['title'], SCREENS[1]['text'], SCREENS[1]['background']),
           '2_level.txt'],
          [(SCREENS[2]['title'], SCREENS[2]['text'], SCREENS[2]['background']),
           '3_level.txt'],
          [(SCREENS[3]['title'], SCREENS[3]['text'], SCREENS[3]['background']),
           '4_level.txt'],
          [(SCREENS[4]['title'], SCREENS[4]['text'], SCREENS[4]['background']),
           '5_level.txt']]

LEVEL_MUSIC = [fir_level_music, sec_level_music, thi_level_music, for_level_music, fif_level_music]
