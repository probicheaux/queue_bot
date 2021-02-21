import queue
import pytest

from queue_bot.api import DiscordBotApi
from discord import User

def start_message(game_name):
    return f"!sqstart {game_name}"

def pop_message(index, game_name):
    return f"!sqpop {index} {game_name}"

def join_message(game):
    return f"!sqjoin {game}"

def leave_message(game):
    return f"!sqleave {game}"

@pytest.fixture(scope='module')
def authors():
    authors = ['a', 'b', 'pete', 'spacey name', '1 name number', 'loser1111111111111']
    for i, name in enumerate(authors):
        user_data = {'username': name,
                     'id': i,
                     'discriminator': name,
                     'avatar': 'http'+ name}

        authors[i] = User(state=None, data=user_data)

    return authors
        
@pytest.fixture(scope='module')
def good_games():
    return ['hi and bi ', 'sup IDIOT12312', 'poop', ';lksfjgs;kjfda;flkdsja;dskjfas;dlkfj']

def test_start(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    author = authors[0]
    start_msg = start_message(good_games[0])
    queue_api.start(start_msg, author)
    assert len(queue_api.queue_list) == 1
    assert len(queue_api.queue_list[0]) == 1

def test_pop(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    author = authors[0]
    start_msg = start_message(good_games[0])
    queue_api.start(start_msg, author)
    assert len(queue_api.queue_list) == 1
    assert len(queue_api.queue_list[0]) == 1
    queue_api.pop(pop_message(1, good_games[0]))
    assert len(queue_api.queue_list) == 0

def test_join_and_leave_by_name(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    for index, game in enumerate(good_games):
        assert len(queue_api.queue_list) == index
        start_msg = start_message(game)
        queue_api.start(start_msg, authors[0])
    
    for game in good_games:
        join_msg = join_message(game)
        for index, author in enumerate(authors[1:]):
            assert len(queue_api.queue_list[game]) == 1 + index
            queue_api.join(join_msg, author)
            
    for game in good_games:
        leave_msg = leave_message(game)
        for index, author in enumerate(authors):
            assert len(queue_api.queue_list[game]) == len(authors) - index
            queue_api.leave(leave_msg, author)
            
    assert len(queue_api.queue_list) == 0

def test_join_and_leave_by_index(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    for index, game in enumerate(good_games):
        assert len(queue_api.queue_list) == index
        start_msg = start_message(game)
        queue_api.start(start_msg, authors[0])
    
    game_names = queue_api.queue_list.games()
    for i, game in enumerate(game_names):
        join_msg = join_message(i+1)
        for index, author in enumerate(authors[1:]):
            assert len(queue_api.queue_list[game]) == 1 + index
            queue_api.join(join_msg, author)
            
    game_names = queue_api.queue_list.games()
    for i, g in enumerate(game_names):
        assert i == queue_api.queue_list.index(g)

    for i, game in enumerate(game_names):
        leave_msg = leave_message(1)
        assert len(queue_api.queue_list) == len(game_names) - i
        for index, author in enumerate(authors):
            assert len(queue_api.queue_list[game]) == len(authors) - index
            queue_api.leave(leave_msg, author)
            
    assert len(queue_api.queue_list) == 0


def test_nuke(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    for index, game in enumerate(good_games):
        assert len(queue_api.queue_list) == index
        start_msg = start_message(game)
        queue_api.start(start_msg, authors[0])
    
    for i, game in enumerate(queue_api.queue_list):
        join_msg = join_message(i+1)
        for index, author in enumerate(authors[1:]):
            assert len(queue_api.queue_list[game]) == 1 + index
            queue_api.join(join_msg, author)

    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
            
def test_clear_by_index(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    for index, game in enumerate(good_games):
        assert len(queue_api.queue_list) == index
        start_msg = start_message(game)
        queue_api.start(start_msg, authors[0])
    
    for i, game in enumerate(queue_api.queue_list):
        join_msg = join_message(i+1)
        for index, author in enumerate(authors[1:]):
            assert len(queue_api.queue_list[game]) == 1 + index
            queue_api.join(join_msg, author)

    for i in range(len(good_games)):
        queue_api.clear('!sclear 1')
    
    assert len(queue_api.queue_list) == 0

def test_clear_by_name(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    for index, game in enumerate(good_games):
        assert len(queue_api.queue_list) == index
        start_msg = start_message(game)
        queue_api.start(start_msg, authors[0])
    
    for i, game in enumerate(queue_api.queue_list):
        join_msg = join_message(i+1)
        for index, author in enumerate(authors[1:]):
            assert len(queue_api.queue_list[game]) == 1 + index
            queue_api.join(join_msg, author)

    for game in good_games:
        queue_api.clear(f'!sclear {game}')
    
    assert len(queue_api.queue_list) == 0

def test_pop(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    game = good_games[0]
    start_msg = start_message(game)
    queue_api.start(start_msg, authors[0])
    for author in authors[1:]:
        join_msg = join_message(game)
        queue_api.join(join_msg, author)

    for index in range(len(authors)):
        assert len(queue_api.queue_list[0]) == len(authors) - index
        queue_api.pop('!sqpop 1 1')

    queue_api.start(start_msg, authors[0])
    for author in authors[1:]:
        join_msg = join_message(game)
        queue_api.join(join_msg, author)


    queue_api.pop(f'!sqpop {len(authors)} 1')
    assert len(queue_api.queue_list) == 0

def test_kick(good_games, authors):
    queue_api = DiscordBotApi()
    queue_api.nuke()
    assert len(queue_api.queue_list) == 0
    game = good_games[0]
    start_msg = start_message(game)
    queue_api.start(start_msg, authors[0])
    for author in authors[1:]:
        join_msg = join_message(game)
        queue_api.join(join_msg, author)

    for index in range(len(authors)):
        assert len(queue_api.queue_list[0]) == len(authors) - index
        queue_api.kick('!sqkick 1 1')

    assert len(queue_api.queue_list) == 0

