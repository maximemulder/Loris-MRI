import os

from lib.dataclass.api import Api


def post_candidate_dicom(
    api: Api,
    cand_id: int,
    psc_id: str,
    visit_label: str,
    is_phantom: bool,
    file_path: str,
    overwrite: bool = False,
):
    json = {
        'CandID':     cand_id,
        'PSCID':      psc_id,
        'VisitLabel': visit_label,
        'IsPhantom':  is_phantom,
        'Overwrite': overwrite,
    }

    response = api.post_file(
        'v0.0.4-dev',
        f'/candidates/{cand_id}/{visit_label}/dicoms',
        json=json,
        files={'File': (os.path.basename(file_path), open(file_path, 'rb'), 'application/tar')},
    )

    return response.text
    # TODO: Handle 303
