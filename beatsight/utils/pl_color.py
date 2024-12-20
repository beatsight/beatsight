"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

PL_COLOR = {
    'Assembly': {'color': '#6E4C13',
                 'rgb': (110, 76, 19),
                 'url': 'https://github.com/trending?l=Assembly'},
    'Awk': {'color': '#c30e9b',
            'rgb': (195, 14, 155),
            'url': 'https://github.com/trending?l=Awk'},
    'C': {'color': '#555555',
          'rgb': (85, 85, 85),
          'url': 'https://github.com/trending?l=CSS'},
    'CMake': {'color': '#DA3434',
              'rgb': (218, 52, 52),
              'url': 'https://github.com/trending?l=CMake'},
    'CSS': {'color': '#563d7c',
            'rgb': (86, 61, 124),
            'url': 'https://github.com/trending?l=CSS'},
    'C++': {'color': '#f34b7d',
            'rgb': (243, 75, 125),
            'url': 'https://github.com/trending?l=CPP'},
    'Dart': {'color': '#00B4AB',
             'rgb': (0, 180, 171),
             'url': 'https://github.com/trending?l=Dart'},
    'Dockerfile': {'color': '#384d54',
                   'rgb': (56, 77, 84),
                   'url': 'https://github.com/trending?l=Dockerfile'},
    'Elixir': {'color': '#6e4a7e',
               'rgb': (110, 74, 126),
               'url': 'https://github.com/trending?l=Elixir'},
    'Erlang': {'color': '#B83998',
               'rgb': (184, 57, 152),
               'url': 'https://github.com/trending?l=Erlang'},
    'Fortran': {'color': '#4d41b1',
                'rgb': (77, 65, 177),
                'url': 'https://github.com/trending?l=Fortran'},
    'Go': {'color': '#00ADD8',
           'rgb': (0, 173, 216),
           'url': 'https://github.com/trending?l=Go'},
    'Groovy': {'color': '#4298b8',
               'rgb': (66, 152, 184),
               'url': 'https://github.com/trending?l=Groovy'},
    'HTML': {'color': '#e34c26',
             'rgb': (227, 76, 38),
             'url': 'https://github.com/trending?l=HTML'},
    'Haskell': {'color': '#5e5086',
                'rgb': (94, 80, 134),
                'url': 'https://github.com/trending?l=Haskell'},
    'Java': {'color': '#b07219',
             'rgb': (176, 114, 25),
             'url': 'https://github.com/trending?l=Java'},
    'JavaScript': {'color': '#f1e05a',
                   'rgb': (241, 224, 90),
                   'url': 'https://github.com/trending?l=JavaScript'},
    'Less': {'color': '#1d365d',
                   'rgb': (29, 54, 93),
                   'url': 'https://github.com/trending?l=less'},
    'Julia': {'color': '#a270ba',
              'rgb': (162, 112, 186),
              'url': 'https://github.com/trending?l=Julia'},
    'Kotlin': {'color': '#A97BFF',
               'rgb': (169, 123, 255),
               'url': 'https://github.com/trending?l=Kotlin'},
    'Lua': {'color': '#000080',
            'rgb': (0, 0, 128),
            'url': 'https://github.com/trending?l=Lua'},
    'MATLAB': {'color': '#e16737',
               'rgb': (225, 103, 55),
               'url': 'https://github.com/trending?l=MATLAB'},
    'Makefile': {'color': '#427819',
                 'rgb': (66, 120, 25),
                 'url': 'https://github.com/trending?l=Makefile'},
    'OCaml': {'color': '#ef7a08',
              'rgb': (239, 122, 8),
              'url': 'https://github.com/trending?l=OCaml'},
    'PHP': {'color': '#4F5D95',
            'rgb': (79, 93, 149),
            'url': 'https://github.com/trending?l=PHP'},
    'Perl': {'color': '#0298c3',
             'rgb': (2, 152, 195),
             'url': 'https://github.com/trending?l=Perl'},
    'PowerShell': {'color': '#012456',
                   'rgb': (1, 36, 86),
                   'url': 'https://github.com/trending?l=PowerShell'},
    'Prolog': {'color': '#74283c',
               'rgb': (116, 40, 60),
               'url': 'https://github.com/trending?l=Prolog'},
    'Python': {'color': '#3572A5',
               'rgb': (53, 114, 165),
               'url': 'https://github.com/trending?l=Python'},
    'R': {'color': '#198CE7',
          'rgb': (25, 140, 231),
          'url': 'https://github.com/trending?l=R'},
    'Racket': {'color': '#3c5caa',
               'rgb': (60, 92, 170),
               'url': 'https://github.com/trending?l=Racket'},
    'Ruby': {'color': '#701516',
             'rgb': (112, 21, 22),
             'url': 'https://github.com/trending?l=Ruby'},
    'Rust': {'color': '#dea584',
             'rgb': (222, 165, 132),
             'url': 'https://github.com/trending?l=Rust'},
    'SCSS': {'color': '#c6538c',
             'rgb': (198, 83, 140),
             'url': 'https://github.com/trending?l=SCSS'},
    'SQL': {'color': '#e38c00',
            'rgb': (227, 140, 0),
            'url': 'https://github.com/trending?l=SQL'},
    'Scala': {'color': '#c22d40',
              'rgb': (194, 45, 64),
              'url': 'https://github.com/trending?l=Scala'},
    'Scheme': {'color': '#1e4aec',
               'rgb': (30, 74, 236),
               'url': 'https://github.com/trending?l=Scheme'},
    'Shell': {'color': '#89e051',
              'rgb': (137, 224, 81),
              'url': 'https://github.com/trending?l=Shell'},
    'Swift': {'color': '#F05138',
              'rgb': (240, 81, 56),
              'url': 'https://github.com/trending?l=Swift'},
    'Tcl': {'color': '#e4cc98',
            'rgb': (228, 204, 152),
            'url': 'https://github.com/trending?l=Tcl'},
    'TypeScript': {'color': '#3178c6',
                   'rgb': (49, 120, 198),
                   'url': 'https://github.com/trending?l=TypeScript'},
    'VBScript': {'color': '#15dcdc',
                 'rgb': (21, 220, 220),
                 'url': 'https://github.com/trending?l=VBScript'}
}
