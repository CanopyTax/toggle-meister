from datetime import datetime

from starlette.responses import JSONResponse
from starlette.requests import Request

from .dataaccess import toggleda
from .dataaccess import releasesda
from . import auditing
from . import permissions


async def get_release_notes_for_env(request: Request) -> JSONResponse:
    params = request.query_params

    env = request.path_params.get('name').lower()
    enrollment_id = params.get('enrollment_id')
    num_of_days = int(params.get('num_of_days', '90'))

    release_notes_data = await releasesda.get_release_notes()
    release_notes = {}
    for r in release_notes_data:
        if r['feature'] not in release_notes:
            release_notes[r['feature']] = [r]
        else:
            release_notes[r['feature']].append(r)

    features = release_notes.keys()

    # Get sort order
    results = await toggleda.get_real_toggle_states(env, features, _with_results=True)
    feature_order = [(row['feature'], row['date_on'])
                     for row in results
                     if row['state'] == 'ON' and
                     (datetime.now() - row['date_on']).days <= num_of_days]

    # add in releases without features
    for _, releases in release_notes.items():
        for release in releases:
            if 'feature' not in release or release['feature'] is None:
                feature_order.append((release['feature'], release['date']))

    feature_order = sorted(feature_order, key=lambda x: x[1], reverse=True)
    feature_order = [a for a, _ in feature_order]

    # now match with toggles this person has on
    toggles = await toggleda.get_toggle_states_for_env(env, features, user_id=enrollment_id)
    toggles = [k for k, v in toggles.items() if v]  # only get ones that are on

    # build the list
    results = []
    for t in toggles:
        if t not in feature_order:
            # get the ones on for this user, but not on globally, put these at the top
            # (not worth sorting by date)
            for r in release_notes.get(t):
                results.append(r)

    for f in feature_order:
        # now go based on sort order
        for r in release_notes.get(f):
            if r not in results:
                results.append(r)

    # finally, make the dates json-able
    for r in results:
        r['date'] = f"{r['date'].year}-{r['date'].month}-{r['date'].day}"

    return JSONResponse({"release_notes": results},
                        headers={'Access-Control-Allow-Origin': '*'})


async def get_all_release_notes(request: Request) -> JSONResponse:
    # dont currently support number of days
    # num_of_days = int(request.query_params.get('num_of_days', '-1'))
    release_note_list = await releasesda.get_release_notes()
    for r in release_note_list:
        r['date'] = f"{r['date'].year}-{r['date'].month}-{r['date'].day}"

    return JSONResponse({'release_notes': release_note_list})


async def create_release_note(request: Request) -> JSONResponse:
    user = request.user.display_name
    request_body = await request.json()
    release_title = request_body.get('title', '').strip()
    feature = request_body.get('feature', '').strip()
    body = request_body.get('body', '').strip()

    await permissions.check_permissions(user, permissions.Action.manage_release_notes)

    if not release_title:
        return JSONResponse({'Message': 'No valid title'}, status_code=400)

    release_note_id = await releasesda.create_release_note(
        release_title, body=body, feature=feature)

    await auditing.audit_event('release_note.create', user,
                               {'id': release_note_id, 'title': release_title,
                                'body': body, 'feature': feature})

    request_body['id'] = release_note_id
    return JSONResponse(request_body)


async def delete_release_note(request: Request) -> JSONResponse:
    user = request.user.display_name
    release_note_id = int(request.path_params.get('id'))

    await permissions.check_permissions(user, permissions.Action.manage_release_notes)

    results = await releasesda.delete_release_note(release_note_id)
    await auditing.audit_event('release_note.delete', user,
                               {'id': release_note_id, 'title': results['title'],
                                'body': results['body'], 'feature': results['feature']})

    return JSONResponse(None, status_code=204)


async def edit_release_note(request: Request) -> JSONResponse:
    user = request.user.display_name
    release_note_id = int(request.path_params.get('id'))
    request_body = await request.json()

    release_title = request_body.get('title', '').strip()
    feature = request_body.get('feature', '').strip()
    body = request_body.get('body', '').strip()

    await permissions.check_permissions(user, permissions.Action.manage_release_notes)

    await releasesda.update_release_note(release_note_id,
                                         title=release_title,
                                         body=body,
                                         feature=feature)

    await auditing.audit_event('release_note.edit', user,
                               {'id': release_note_id, 'title': release_title,
                                'body': body, 'feature': feature})

    return JSONResponse(request_body)
