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


async def get_tutor_data_from_crm(phone: str, branch: str = None) -> Optional[Dict[str, Any]]:
    """
    Get tutor data from external CRM system using the old get_teacher logic
    """
    if not branch or not settings.crm_api_key:
        return None

    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None

    # Use the branch from tutor profile to construct the URL
    url = f"{settings.crm_api_url}/v2api/{branch}/teacher/index"
    data = {"phone": phone}  # Using ID instead of phone as in the original example

    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            items = result.get("items", [])
            if items:
                return items[0]
            return None
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


async def get_client_data_from_crm(student_crm_id: str, branch: str = None) -> Optional[Dict[str, Any]]:
    """
    Get client data from external CRM system using the old find_client_by_id logic
    """
    if not branch or not settings.crm_api_key:
        return None
    
    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None
    
    # Use the branch from tutor profile to construct the URL
    url = f"{settings.crm_api_url}/v2api/{branch}/customer/index"
    # Using the logic from find_client_by_id function
    data = {"id": student_crm_id, "is_study": 2, "page": 0}  # 1 - clients, 0 - leads, 2 - all
    
    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Check if response has items
            clients = result.get("items", [])
            
            if not clients:
                return None

            if len(clients) > 1:
                # Return the first client if multiple found
                pass

            return clients[0]
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


async def get_tutor_groups_from_crm(tutor_crm_id: str, branch: str = None) -> Optional[Dict[str, Any]]:
    """
    Get tutor groups from external CRM system using the old get_teacher_groups logic
    """
    if not branch or not settings.crm_api_key:
        return None
    
    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None
    
    url = f"{settings.crm_api_url}/v2api/{branch}/group/index"
    data = {"teacher_id": tutor_crm_id}
    
    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            all_groups = result.get("items", [])
            if all_groups:
                teacher_id_int = int(tutor_crm_id) if tutor_crm_id.isdigit() else tutor_crm_id
                filtered_groups = []
                for group in all_groups:
                    # Check if the teacher is in this group by looking at the teachers list
                    teachers = group.get("teachers", [])
                    if any(teacher.get("id") == teacher_id_int for teacher in teachers):
                        filtered_groups.append(group)
                return filtered_groups
            return None
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


async def get_group_clients_from_crm(group_id: str, branch: str = None) -> Optional[Dict[str, Any]]:
    """
    Get clients in a group from external CRM system using the old get_clients_in_group logic
    """
    if not branch or not settings.crm_api_key:
        return None

    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None

    url = f"{settings.crm_api_url}/v2api/{branch}/cgi/index"
    params = {"group_id": group_id}

    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            customer_ids = [customer_id["customer_id"] for customer_id in result.get("items", [])]
            client_names = []

            # For each customer_id, get client data
            for customer_id in customer_ids:
                # Note: This is recursive and might need to be optimized
                client_data = await get_client_data_from_crm(str(customer_id), branch)
                if client_data:
                    client_name = client_data.get("name", "Неизвестный клиент")
                    client_names.append(client_name)
                else:
                    client_names.append("Клиент не найден")

            # Create the response format
            clients_in_group = [{"customer_id": customer_id, "client_name": client_name}
                               for customer_id, client_name in zip(customer_ids, client_names)]
            return clients_in_group
        except httpx.HTTPStatusError:
            # Handle HTTP errors
            return None
        except httpx.RequestError:
            # Handle request errors
            return None


async def get_all_groups() -> Optional[Dict[str, Any]]:
    """
    Get all groups from external CRM system
    """
    if not settings.crm_api_key:
        return None
    
    # Get token for authentication
    token = await login_to_alfa_crm()
    if not token:
        return None
    
    all_items = []
    branches = [1, 2, 3, 4]  # Default to 1-4 if not specified
    
    headers = {**BASE_HEADERS, "X-ALFACRM-TOKEN": token}
    
    for branch in branches:
        page = 0
        
        while True:
            # Construct the URL for the current branch and page
            url = f"{settings.crm_api_url}/v2api/{branch}/group/index"
            data = {"page": page, "limit": 50}  # Assuming API supports pagination
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    result = response.json()
                    
                    items = result.get("items", [])
                    current_page_count = len(items)
                    total = result.get("total", 0)
                    
                    if current_page_count == 0:
                        break  # No more data
                    
                    all_items.extend(items)
                    page += 1
                    
                    # Additional protection: if we've collected all records
                    if len(all_items) >= total > 0:
                        break
                except httpx.HTTPStatusError:
                    # Handle HTTP errors
                    break
                except httpx.RequestError:
                    # Handle request errors
                    break
    
    return all_items
