import csv
import json
import os
import requests

# URL base activa de tu entorno en Urban Grocers
BASE_URL = (
    "https://cnt-06a4a205-6972-4282-8db9-fc768c0022a7.containerhub.tripleten-services.com"
)

# ID del kit fijo para esta sesión de pruebas
FIXED_KIT_ID = 7


def create_user_and_get_token():
  """Crea un usuario nuevo en el sistema y retorna su token de autorización."""
  url = f"{BASE_URL}/api/v1/users"
  headers = {"Content-Type": "application/json"}
  payload = {
      "firstName": "Eugenio",
      "phone": "+11234567890",
      "address": "Hermosillo, Sonora",
  }
  response = requests.post(url, json=payload, headers=headers)
  if response.status_code == 201:
    token = response.json().get("authToken")
    print(f"👤 Usuario creado con éxito. Token obtenido: {token}")
    return token
  raise Exception(f"Error al crear usuario: {response.text}")


def generate_jira_bug_report(
    test_id,
    test_name,
    endpoint,
    method,
    payload,
    expected_status,
    actual_status,
    response_body,
    error_detail="",
):
  print("\n" + "=" * 70)
  print(f" 🐛 BUG REPORT GENERADO AUTOMÁTICAMENTE PARA JIRA (Caso #{test_id}) ")
  print("=" * 70)
  print(
      f"**Título:** [{method} {endpoint}] - {test_name} | Esperado: HTTP"
      f" {expected_status}, Obtenido: HTTP {actual_status}"
  )
  print("**Entorno:** QA Environment / Linux Terminal (Python Automated)")
  print("**Prioridad:** Medium / High")
  if error_detail:
    print(f"\n⚠️ **Detalle del fallo:** {error_detail}")
  print("\n**Pasos para reproducir:**")
  print(f"1. Enviar petición HTTP {method} a la ruta `{endpoint}`.")
  print("2. Configurar los encabezados incluyendo el token de autorización.")
  if payload is not None:
    print(
        "3. Enviar el siguiente cuerpo de solicitud"
        f" (Payload):\n```json\n{json.dumps(payload, indent=4)}\n```"
    )
  print(f"\n**Resultado Esperado:** Código HTTP {expected_status}.")
  print(
      f"**Resultado Actual:** Código HTTP {actual_status}.\nCuerpo de la"
      f" respuesta:\n```json\n{response_body}\n```"
  )
  print("=" * 70 + "\n")


def get_test_suite(kit_id, auth_token):
  """Define la suite de pruebas usando explícitamente el Kit ID fijo y el token en los headers."""
  common_headers = {
      "Content-Type": "application/json",
      "Authorization": auth_token,
  }

  return [
      {
          "id": 1,
          "name": (
              "Verificar que el usuario pueda añadir un producto existente a un"
              " kit"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 3, "quantity": 3}]},
          "expected_status": 200,
      },
      {
          "id": 2,
          "name": (
              "Verificar que se puedan agregar múltiples productos únicos"
              " existentes a un kit"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {
              "productsList": [
                  {"id": 1, "quantity": 2},
                  {"id": 6, "quantity": 3},
              ]
          },
          "expected_status": 200,
      },
      {
          "id": 3,
          "name": (
              "Verificar el límite máximo permitido de 30 productos únicos en"
              " un kit (BVA Positivo)"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {
              "productsList": [{"id": i, "quantity": 1} for i in range(1, 31)]
          },
          "expected_status": 200,
      },
      {
          "id": 4,
          "name": (
              "Verificar el comportamiento al intentar agregar 31 productos"
              " únicos a un kit superando el límite (BVA Negativo)"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {
              "productsList": [{"id": i, "quantity": 1} for i in range(1, 32)]
          },
          "expected_status": 400,
          "expected_error_message": "No más de 30 artículos por conjunto",
      },
      {
          "id": 5,
          "name": (
              "Verificar el comportamiento al intentar agregar productos a un"
              " ID de kit no existente"
          ),
          "method": "POST",
          "endpoint": "/api/v1/kits/9999/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": 1}]},
          "expected_status": 404,
      },
      {
          "id": 6,
          "name": (
              "Verificar el comportamiento al intentar agregar un ID de"
              " producto que no existe en el sistema"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 9999, "quantity": 1}]},
          "expected_status": 400,
      },
      {
          "id": 7,
          "name": (
              "Verificar el comportamiento al enviar una cantidad de producto"
              " negativa"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": -1}]},
          "expected_status": 400,
      },
      {
          "id": 8,
          "name": (
              "Verificar el comportamiento al enviar una cantidad igual a cero"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": 0}]},
          "expected_status": 400,
      },
      {
          "id": 9,
          "name": (
              "Verificar el comportamiento cuando productsList no es un arreglo"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": {"id": 1, "quantity": 1}},
          "expected_status": 400,
      },
      {
          "id": 10,
          "name": (
              "Verificar el comportamiento al enviar un cuerpo de solicitud"
              " JSON totalmente vacío"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {},
          "expected_status": 400,
      },
      {
          "id": 11,
          "name": (
              "Verificar la adición de 1 solo producto único a un kit (Límite"
              " inferior BVA Positivo)"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": 1}]},
          "expected_status": 200,
      },
      {
          "id": 12,
          "name": (
              "Verificar el comportamiento al enviar un arreglo productsList"
              " vacío (BVA Negativo)"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": []},
          "expected_status": 400,
      },
      {
          "id": 13,
          "name": (
              "Verificar que una cantidad alta (quantity: 35) no afecte el"
              " límite de productos únicos"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": 35}]},
          "expected_status": 200,
      },
      {
          "id": 14,
          "name": (
              "Verificar el comportamiento al enviar un tipo string en el"
              " parámetro ID del kit"
          ),
          "method": "POST",
          "endpoint": "/api/v1/kits/abc/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": 1}]},
          "expected_status": 400,
      },
      {
          "id": 15,
          "name": (
              "Verificar el comportamiento al enviar un string en el campo id"
              " de producto"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": "uno", "quantity": 1}]},
          "expected_status": 400,
      },
      {
          "id": 16,
          "name": (
              "Verificar la adición de 29 productos únicos a un kit (Límite"
              " cercano al máximo)"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {
              "productsList": [{"id": i, "quantity": 1} for i in range(1, 30)]
          },
          "expected_status": 200,
      },
      {
          "id": 17,
          "name": (
              "Verificar el comportamiento al enviar el mismo ID de producto"
              " repetido"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {
              "productsList": [
                  {"id": 1, "quantity": 2},
                  {"id": 1, "quantity": 3},
              ]
          },
          "expected_status": 200,
      },
      {
          "id": 18,
          "name": (
              "Verificar el comportamiento al omitir la propiedad id en el"
              " objeto de producto"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"quantity": 2}]},
          "expected_status": 400,
      },
      {
          "id": 19,
          "name": (
              "Verificar el comportamiento al omitir la propiedad quantity en"
              " el objeto de producto"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1}]},
          "expected_status": 400,
      },
      {
          "id": 20,
          "name": (
              "Verificar el comportamiento al enviar un string en el campo"
              " quantity"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": "dos"}]},
          "expected_status": 400,
      },
      {
          "id": 21,
          "name": (
              "Verificar el comportamiento al enviar método GET en lugar de"
              " POST"
          ),
          "method": "GET",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": None,
          "expected_status": 405,
      },
      {
          "id": 22,
          "name": (
              "Verificar robustez ante inyección maliciosa en el parámetro ID"
              " de kit"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}%27%20OR%20%271%27=%271/products",
          "headers": common_headers,
          "payload": {"productsList": [{"id": 1, "quantity": 1}]},
          "expected_status": 400,
      },
      {
          "id": 23,
          "name": (
              "Verificar comportamiento al incluir campos extra no"
              " documentados en el body"
          ),
          "method": "POST",
          "endpoint": f"/api/v1/kits/{kit_id}/products",
          "headers": common_headers,
          "payload": {
              "isAdmin": True,
              "discountCode": "FREE_KIT",
              "productsList": [{"id": 1, "quantity": 1}],
          },
          "expected_status": 200,
      },
  ]


def run_kits_tests():
  try:
    # 1. Crear usuario y obtener token fresco
    auth_token = create_user_and_get_token()
    kit_id = FIXED_KIT_ID
    print(
        f"📦 Usando Kit ID fijo '{kit_id}' para la sesión con token"
        f" autogenerado."
    )
  except Exception as e:
    print(f"❌ Error crítico en la preparación del entorno: {e}")
    return

  test_suite = get_test_suite(kit_id, auth_token)
  results_data = []
  failed_tests = 0
  passed_tests = 0

  print(
      f"\n🚀 Iniciando ejecución automatizada de {len(test_suite)} casos de"
      f" prueba sobre el Kit ID {kit_id}..."
  )
  print("=" * 70)

  for case in test_suite:
    url = f"{BASE_URL}{case['endpoint']}"
    method = case["method"]
    headers = case["headers"]
    payload = case["payload"]
    expected_status = case["expected_status"]
    expected_error_msg = case.get("expected_error_message")

    try:
      if method == "POST":
        response = requests.post(url, json=payload, headers=headers)
      elif method == "GET":
        response = requests.get(url, headers=headers)
      else:
        continue

      actual_status = response.status_code

      try:
        resp_body = response.json()
        resp_text = json.dumps(resp_body, indent=4, ensure_ascii=False)
      except Exception:
        resp_body = {}
        resp_text = response.text

      http_matched = actual_status == expected_status
      message_matched = True
      error_detail = ""

      if http_matched and expected_error_msg:
        resp_message = (
            resp_body.get("message", "") if isinstance(resp_body, dict) else ""
        )
        if expected_error_msg not in resp_message:
          message_matched = False
          error_detail = (
              f"Se esperaba el mensaje de error '{expected_error_msg}', pero se"
              f" obtuvo '{resp_message}'."
          )

      status_matched = http_matched and message_matched

      if status_matched:
        passed_tests += 1
        status_label = "Passed"
        actual_result_text = (
            f"El sistema devolvió el código esperado HTTP {actual_status} y"
            " validó correctamente la restricción."
        )
      else:
        failed_tests += 1
        status_label = "Failed"
        actual_result_text = (
            f"El sistema devolvió HTTP {actual_status}, en lugar de rechazar"
            f" con el código esperado HTTP {expected_status}."
        )
        error_detail = (
            f"Código esperado: {expected_status}, obtenido: {actual_status}."
        )

      results_data.append({
          "ID": case["id"],
          "Nombre": case["name"],
          "Estatus": status_label,
          "Estado Esperado": expected_status,
          "Estado Obtenido": actual_status,
          "Resultado Obtenido Redactado": actual_result_text,
      })

      print(f"  [{status_label.upper()}] Caso #{case['id']}: {case['name']}")
      print(f"    └─ Resultado Obtenido: {actual_result_text}\n")

      if not status_matched:
        generate_jira_bug_report(
            test_id=case["id"],
            test_name=case["name"],
            endpoint=case["endpoint"],
            method=method,
            payload=payload,
            expected_status=expected_status,
            actual_status=actual_status,
            response_body=resp_text,
            error_detail=error_detail,
        )

    except requests.exceptions.RequestException as e:
      failed_tests += 1
      print(f"  [ERROR] Caso #{case['id']} falló por excepción de red: {e}\n")

  print("=" * 70)
  print(f"📊 RESUMEN FINAL (KITS): {passed_tests} PASSED, {failed_tests} FAILED.")
  print("=" * 70 + "\n")

  os.makedirs("Artifacts/Reports", exist_ok=True)
  csv_path = os.path.join("Artifacts", "Reports", "kits_results.csv")
  with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "ID",
        "Nombre",
        "Estatus",
        "Estado Esperado",
        "Estado Obtenido",
        "Resultado Obtenido Redactado",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results_data)

  print(f"📁 Reporte CSV de kits exportado con éxito a: {csv_path}")

  del test_suite
  del results_data


if __name__ == "__main__":
  run_kits_tests()
