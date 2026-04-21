from dataclasses import dataclass
from typing import Optional

from admin_api.clients.modalities_service import StaffDTO, modalities_service_client


@dataclass
class Staff:
    id: int
    full_name: str
    staff_number: Optional[str]
    contact: Optional[str]


class StaffService:

    def _build_staff_from_data(self, data: StaffDTO) -> Staff:
        return Staff(
            id=data.id,
            full_name=data.full_name,
            staff_number=data.staff_number,
            contact=data.contact,
        )

    def list_staff(self):
        data = modalities_service_client.staff.list_staff()
        return [self._build_staff_from_data(item) for item in data]

    def create_staff(self, full_name, staff_number, contact):
        data = modalities_service_client.staff.create_staff(
            full_name, staff_number, contact
        )
        return self._build_staff_from_data(data)

    def get_staff(self, staff_id):
        data = modalities_service_client.staff.get_staff(staff_id)
        return self._build_staff_from_data(data)

    def update_staff(self, staff_id, full_name, staff_number, contact):
        data = modalities_service_client.staff.update_staff(
            staff_id, full_name, staff_number, contact
        )
        return self._build_staff_from_data(data)

    def delete_staff(self, staff_id):
        return modalities_service_client.staff.delete_staff(staff_id)


staff_service = StaffService()
