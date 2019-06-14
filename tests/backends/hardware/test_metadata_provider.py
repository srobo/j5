def mock_iglob(pattern):
  assert pattern == "/test/*.json"
  return iter([
    "/test/1.json",
    "/test/2.json",
  ])

def test_discover() -> None:
  found_boards = MetadataProviderFilesystemBackend.discover("/test/*.json", iglob=mock_iglob)
  assert len(found_boards) == 2
  assert all(type(board) is MetadataProvider for board in found_boards)

def test_discover_serials():
  found_boards = MetadataProviderFilesystemBackend.discover("/test/*.json", iglob=mock_iglob)
  serials = {board.serial for board in found_boards}
  assert serials == {"/test/1.json", "/test/2.json"}


