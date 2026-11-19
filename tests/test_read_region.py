import io
import secrets

from orbispanora_lib.anvil import Region


class TestReadRegion:

    def test_from_filename(self, tmp_path):
        filename = tmp_path / "r.0.0.mca"
        contents = secrets.token_bytes()

        with open(filename, 'wb') as f:
            f.write(contents)

        region = Region.from_file(str(filename))
        assert region.data == contents

    def test_from_filelike(self):
        contents = secrets.token_bytes()
        filelike = io.BytesIO(contents)

        region = Region.from_file(filelike)
        assert region.data == contents
