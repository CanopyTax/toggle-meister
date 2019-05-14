import asyncio

from pytest import fixture
from starlette.testclient import TestClient

from tmeister import core


@fixture(scope='session')
def app():
    app = core.init()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(core.pg_init())
    return app


@fixture(scope='module')
def client(app):
    return TestClient(app)


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_get_envs(client):
    response = client.get('/api/envs')
    envs = [e['name'] for e in response.json()['envs']]
    assert 'production' in envs


def test_invalid_post_json(client):
    response = client.post('/api/envs',
                           data='{"name": "bob}',
                           headers={'Content-Type': 'application/json'})
    assert response.status_code == 400


def test_adding_env(client):
    response = client.post('/api/envs',
                           json={'name': 'bob2'})
    assert response.json()['name'] == 'bob2'


def test_getting_env(client):
    response = client.get('/api/envs')
    assert len([e for e in response.json()['envs'] if e['name'] == 'bob2']) > 0


def test_adding_already_existing_env(client):
    response = client.post('/api/envs',
                           json={'name': 'bob2'})
    assert response.status_code == 409


def test_add_feature(client):
    response = client.post('/api/features', json={'name': 'bobbytables'})
    assert response.json()['name'] == 'bobbytables'


def test_get_features(client):
    response = client.get('/api/features')
    assert len([f for f in response.json()['features'] if f['name'] == 'bobbytables']) > 0


def test_get_toggles(client):
    response = client.get('/api/toggles')
    toggle = [t for t in response.json()['toggles']
              if t['toggle']['env'] == 'bob2' and t['toggle']['feature'] == 'bobbytables'][0]
    assert toggle['toggle']['state'] == 'OFF'


def test_get_single_toggle(client):
    response = client.get('/api/envs/bob2/toggles?feature=bobbytables')
    assert response.json()['bobbytables'] == False  # noqa


def test_turn_toggle_on(client):
    response = client.patch(
        '/api/toggles',
        json={'toggle': {'env': 'bob2', 'feature': 'bobbytables', 'state': 'ON'}})

    toggle = [t for t in response.json()['toggles']
              if t['toggle']['env'] == 'bob2' and t['toggle']['feature'] == 'bobbytables'][0]
    assert toggle['toggle']['state'] == 'ON'


def test_get_single_toggle_on(client):
    response = client.get('/api/envs/bob2/toggles?feature=bobbytables')
    assert response.json()['bobbytables'] == True  # noqa


def test_turn_toggle_on_thats_already_on(client):
    # should work fine, no error
    response = client.patch(
        '/api/toggles',
        json={'toggle': {'env': 'bob2', 'feature': 'bobbytables', 'state': 'ON'}})

    toggle = [t for t in response.json()['toggles']
              if t['toggle']['env'] == 'bob2' and t['toggle']['feature'] == 'bobbytables'][0]
    assert toggle['toggle']['state'] == 'ON'


def test_get_toggles_again(client):
    response = client.get('/api/toggles')
    toggle = [t for t in response.json()['toggles']
              if t['toggle']['env'] == 'bob2' and t['toggle']['feature'] == 'bobbytables'][0]
    assert toggle['toggle']['state'] == 'ON'


def test_add_another_feature(client):
    response = client.post('/api/features', json={'name': 'bobbytables2'})
    assert response.json()['name'] == 'bobbytables2'


def test_get_multiple_env_toggles(client):
    response = client.get('/api/envs/bob2/toggles?feature=bobbytables&feature=bobbytables2')
    assert response.status_code == 200
    r = response.json()
    assert r['bobbytables'] == True  # noqa
    assert r['bobbytables2'] == False  # noqa


def test_turn_toggle_off(client):
    response = client.patch(
        '/api/toggles',
        json={'toggle': {'env': 'bob2', 'feature': 'bobbytables', 'state': 'OFF'}})

    toggle = [t for t in response.json()['toggles']
              if t['toggle']['env'] == 'bob2' and t['toggle']['feature'] == 'bobbytables'][0]
    assert toggle['toggle']['state'] == 'OFF'


def test_turn_toggle_on_for_production(client):
    # should turn all toggles on for other envs
    response = client.patch(
        '/api/toggles',
        json={'toggle': {'env': 'production', 'feature': 'bobbytables', 'state': 'ON'}})

    toggle = [t for t in response.json()['toggles']
              if t['toggle']['env'] == 'bob2' and t['toggle']['feature'] == 'bobbytables'][0]
    assert toggle['toggle']['state'] == 'ON'

    toggle = [t for t in response.json()['toggles']
              if t['toggle']['env'] == 'production' and t['toggle']['feature'] == 'bobbytables'][0]
    assert toggle['toggle']['state'] == 'ON'


def test_get_audit_logs(client):
    response = client.get('/api/auditlog')
    assert response.status_code == 200


def test_turn_toggles_off(client):
    response = client.patch(
        '/api/toggles',
        json={'toggle': {'env': 'production', 'feature': 'bobbytables', 'state': 'OFF'}})
    assert response.status_code == 200

    response = client.patch(
        '/api/toggles',
        json={'toggle': {'env': 'bob2', 'feature': 'bobbytables', 'state': 'OFF'}})
    assert response.status_code == 200


def test_soft_delete_feature(client):
    # first set toggle to on
    response = client.patch(
        '/api/toggles',
        json={'toggle': {'env': 'bob2', 'feature': 'bobbytables', 'state': 'ON'}})

    # now delete feature
    response = client.delete('/api/features/bobbytables')
    assert response.status_code == 204

    # now get toggles - should still be "on"
    response = client.get('/api/envs/bob2/toggles?feature=bobbytables')
    assert response.json()['bobbytables'] == True  # noqa


def test_creating_feature_that_is_soft_deleted(client):
    # creating a feature that is soft deleted should work
    response = client.post('/api/features', json={'name': 'bobbytables'})
    assert response.json()['name'] == 'bobbytables'


def test_delete_features(client):
    response = client.delete('/api/features/bobbytables?hard=true')
    assert response.status_code == 204

    response = client.delete('/api/features/bobbytables2?hard=true')
    assert response.status_code == 204


def test_delete_env(client):
    response = client.delete('/api/envs/bob2')
    assert response.status_code == 204
