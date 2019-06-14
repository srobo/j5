import glob

class MetadataProviderFilesystemBackend(MetadataProviderInterface, Backend):
  environment = HardwareEnvironment
  board = MetadataProvider

  @classmethod
  def discover(cls, glob_pattern: str, iglob: Callable = glob.iglob) -> Set[Board]:
    return set(cls._discover_board(path) for path in iglob(glob_pattern))

  @classmethod
  def _discover_board(cls, path: str) -> Board:
    backend = cls(pathlib.Path(path))
    board = MetadataProvider(path, backend)
    return cast(Board, board)

  def __init__(self, path: pathlib.Path):
    self._path = path

  @property
  def firmware_version(self) -> None:
    return None

  def get_metadata(self) -> Metadata:
    with open(self.path, "r") as file:
      obj = json.load(file)
    return self._validate_metadata(obj)

  def _validate_metadata(self, obj: Any) -> Metadata:
    if isinstance(obj, dict):
      for key, value in obj.items():
        if not isinstance(key, str) or not isinstance(value, str):
          raise TypeError
    else:
      raise TypeError
    return obj
