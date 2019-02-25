from typing import List

class USBContext:
  def getDeviceList(self, skip_on_error: bool = False) -> List[USBDevice]: ...

class USBDevice:
  def getVendorID(self) -> int: ...
  def getProductID(self) -> int: ...
  def getSerialNumber(self) -> str: ...
  def open(self) -> USBDeviceHandle: ...

class USBDeviceHandle:
  def controlWrite(self,
    request_type: int,
    request: int,
    value: int,
    index: int,
    data: bytes,
    timeout: int = 0,
  ) -> int: ...
  def controlRead(self,
    request_type: int,
    request: int,
    value: int,
    index: int,
    length: int,
    timeout: int = 0,
  ) -> bytes: ...
