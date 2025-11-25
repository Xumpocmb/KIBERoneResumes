import httpx
from typing import Optional, Dict, Any
from config import settings
from models import TutorProfile


BASE_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "application/json, text/plain, */*",
}


async def login_to_alfa_crm() -> Optional[str]:
    """
    Авторизация в CRM и получение токена.
    """
    if not settings.crm_api_url or not settings.crm_email or not settings.crm_api_key:
        return None

    data = {"email": settings.crm_email, "api_key": settings.crm_api_key}
    # Remove the "https://" prefix and any trailing slashes to construct the proper URL
    base_url = settings.crm_api_url.rstrip('/')
    url = f"{base_url}/v2api/auth/login"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=BASE_HEADERS, json=data)

            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("token")
                return token
            else:
                return None
    except Exception as e:
        return None


async def get_tutor_data_from_crm(tutor_crm_id: str) -> Optional[Dict[str, Any]]:
    """
    Get tutor data from external CRM system
    """
    if not settings.crm_api_url or not settings.crm_api_key:
        return None
    
    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None
    
    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.crm_api_url}/tutors/{tutor_crm_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


async def get_client_data_from_crm(student_crm_id: str) -> Optional[Dict[str, Any]]:
    """
    Get client data from external CRM system
    """
    if not settings.crm_api_url or not settings.crm_api_key:
        return None
    
    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None
    
    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.crm_api_url}/students/{student_crm_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


async def get_tutor_groups_from_crm(tutor_crm_id: str) -> Optional[Dict[str, Any]]:
    """
    Get tutor groups from external CRM system
    """
    if not settings.crm_api_url or not settings.crm_api_key:
        return None
    
    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None
    
    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.crm_api_url}/tutors/{tutor_crm_id}/groups",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


async def get_group_clients_from_crm(group_id: str) -> Optional[Dict[str, Any]]:
    """
    Get clients in a group from external CRM system
    """
    if not settings.crm_api_url or not settings.crm_api_key:
        return None

    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None

    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.crm_api_url}/groups/{group_id}/clients",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


######################################
# old code
####################################


# def get_all_clients(branch_id):
#     url = f"https://{CRM_HOSTNAME}/v2api/{branch_id}/customer/index"

#     page = 0
#     count = 1

#     while count > 0:
#         data = {"is_study": 0, "page": page}
#         clients_response = send_request_to_crm(url=url, data=data, params=None)

#         if not clients_response:
#             logger.error(f"Не удалось получить клиентов для филиала {branch_id}, страница {page}")
#             break

#         if "items" in clients_response:
#             clients = clients_response["items"]
#             count = clients_response.get("count", 0)
#             logger.info(f"Получено {len(clients)} клиентов для филиала {branch_id}, страница {page}")

#             # Возвращаем клиентов по одному через yield
#             for client in clients:
#                 yield client

#         else:
#             logger.error(f"Неверный формат ответа от CRM для филиала {branch_id}, страница {page}")
#             break

#         page += 1

#     logger.info(f"Завершено получение клиентов для филиала {branch_id}")


# get_tutor_data_from_crm - должна использовать код get_teacher()
# def get_teacher(branch, phone_number):
#     url = f"https://kiberoneminsk.s20.online/v2api/{branch}/teacher/index"
#     data = {"phone": phone_number}
#     response = send_request_to_crm(url=url, data=data, params=None)
#     return response


# get_tutor_groups_from_crm - использует код get_teacher_groups()
# def get_teacher_groups(branch, teacher_id):
#     url = f"https://kiberoneminsk.s20.online/v2api/{branch}/group/index"

#     data = {"teacher_id": teacher_id}

#     groups_res = send_request_to_crm(url=url, data=data, params=None)
#     all_groups = groups_res.get("items", [])
#     if all_groups:
#         teacher_id_int = int(teacher_id)
#         filtered_groups = []
#         for group in all_groups:
#             if any(teacher["id"] == teacher_id_int for teacher in group.get("teachers", [])):
#                 filtered_groups.append(group)
#         return filtered_groups
#     return None


# get_group_clients_from_crm использует get_clients_in_group()
# def get_clients_in_group(group_id, branch):
#     url = f"https://kiberoneminsk.s20.online/v2api/{branch}/cgi/index?group_id={group_id}"

#     cgi_res = send_request_to_crm(url=url, data=None, params=None)
#     customer_ids = [customer_id["customer_id"] for customer_id in cgi_res.get("items", [])]
#     client_names = []

#     for customer_id in customer_ids:
#         client_data = find_client_by_id(branch, int(customer_id))
#         if client_data:
#             client_name = client_data.get("name", "Неизвестный клиент")
#             client_names.append(client_name)
#         else:
#             client_names.append("Клиент не найден")

#     clients_in_group = [{"customer_id": customer_id, "client_name": client_name} for customer_id, client_name in zip(customer_ids, client_names)]
#     return clients_in_group


# def get_all_groups():
#     try:
#         branches_ = Branch.objects.all()
#     except Branch.DoesNotExist:
#         return []

#     all_items = []
#     for branch in branches_:
#         url = f"https://kiberoneminsk.s20.online/v2api/{branch.branch_id}/group/index"
#         page = 0

#         while True:
#             response: dict = send_request_to_crm(url=url, data={"page": page}, params=None)
#             items = response.get("items", [])
#             current_page_count = len(items)  # или response.get("count", 0), если API возвращает это поле
#             total = response.get("total", 0)

#             if current_page_count == 0:
#                 break  # больше нет данных

#             all_items.extend(items)
#             page += 1

#             # Дополнительная защита: если уже собрали все записи
#             if len(all_items) >= total > 0:
#                 break

#     return all_items


# get_client_data_from_crm должна использовать код find_client_by_id()
# def find_client_by_id(branch_id, crm_id) -> dict | None:
#     # Добавляем обязательные параметры фильтрации
# branch_id - берем у тьютора. TutorProfile - поле branch
#     data = {"id": crm_id, "is_study": 2, "page": 0}  # 1 - клиенты, 0 - лиды, 2 - все

#     url = f"https://{CRM_HOSTNAME}/v2api/{branch_id}/customer/index"

#     try:
#         response = send_request_to_crm(url=url, data=data, params=None)

#         if not response:
#             logger.error("Пустой ответ от CRM")
#             return None

#         # Проверяем наличие items в ответе
#         clients = response.get("items", [])

#         if not clients:
#             logger.error(f"Клиент с ID {crm_id} не найден")
#             return None

#         if len(clients) > 1:
#             logger.warning(f"Найдено несколько клиентов с ID {crm_id}, возвращаем первого")

#         logger.info(f"Клиент {crm_id} успешно найден")
#         return clients[0]

#     except Exception as e:
#         logger.error(f"Ошибка при поиске клиента: {e}")
#         return None
