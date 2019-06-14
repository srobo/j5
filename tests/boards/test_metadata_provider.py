class MockMetadataProviderBackend(MetadataProviderInterface, Backend):
  def get_metadata(self) -> Metadata:
    return {
      "environment": "comp",
      "corner": "1",
    }

def test_instantiation() -> None:
  MetadataProvider("SERIAL0", MockMetadataProviderBackend())

def test_name() -> None:
  mp = MetadataProvider("SERIAL0", MockMetadataProviderBackend())
  assert mp.name == "Metadata provider"

def test_serial() -> None:
  mp = MetadataProvider("SERIAL0", MockMetadataProviderBackend())
  assert mp.serial == "SERIAL0"

def test_firmware_version() -> None:
  mp = MetadataProvider("SERIAL0", MockMetadataProviderBackend())
  assert mp.firmware_version is None

def test_make_safe() -> None:
  mp = MetadataProvider("SERIAL0", MockMetadataProviderBackend())
  mp.make_safe()

def test_metadata() -> None:
  mp = MetadataProvider("SERIAL0", MockMetadataProviderBackend())
  assert type(mp.metadata) is dict
  assert mp.metadata == {
    "environment": "comp",
    "corner": "1",
  }
