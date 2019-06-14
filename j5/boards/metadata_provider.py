Metadata = Dict[str, str]

class MetadataProviderInterface(Interface):
  @abstractmethod
  def get_metadata(self) -> Metadata:
    raise NotImplementedError

class MetadataProvider(Board):
  def __init__(self, serial: str, backend: MetadataProviderInterface):
    self._serial = serial
    self._backend = backend

  @property
  def name(self) -> str:
    return "Metadata provider"

  @property
  def serial(self) -> str:
    return self._serial

  @property
  def firmware_version(self) -> None:
    return None

  def make_safe(self) -> None:
    pass

  @staticmethod
  def supported_component() -> Set[Type['Component']]:
    return set()

  @property
  def metadata(self) -> Metadata:
    return self._backend.get_metadata()
