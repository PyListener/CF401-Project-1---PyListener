def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('manage', '/manage/{id:\w+}')
    config.add_route('register', '/register')
    config.add_route('category', '/category/{add_id:\d+}')
    config.add_route('attribute', '/attribute/{add_id:\d+}/{cat_id:\d+}')
    config.add_route('display', '/display/{add_id:\d+}/{cat_id:\d+}/{att_id:\d+}')
    config.add_route('test_img', 'test/{id:\d+}')
    config.add_route('picture', '/pic/{db_id:\w+}/{pic_id:\d+}')