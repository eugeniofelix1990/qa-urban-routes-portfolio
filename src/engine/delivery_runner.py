import json
import os
import csv
import requests

# URL base activa del servidor de Urban Grocers (actualizada)
BASE_URL = "https://cnt-1497f28f-5497-45de-837e-b1164acef6b1.containerhub.tripleten-services.com"

def generate_jira_bug_report(test_id, test_name, endpoint, method, payload, expected_status, actual_status, response_body, business_error=""):
    """Genera la estructura del Bug Report formateada para Jira."""
    print("\n" + "=" * 70)
    print(f" 🐛 BUG REPORT GENERADO AUTOMÁTICAMENTE PARA JIRA (Caso #{test_id}) ")
    print("=" * 70)
    print(f"**Título:** [{method} {endpoint}] - {test_name} | Esperado: HTTP {expected_status}, Obtenido: HTTP {actual_status}")
    print("**Entorno:** QA Environment / Linux Terminal (Python Automated)")
    print("**Prioridad:** Medium / High")
    if business_error:
        print(f"\n⚠️ **Falla de Negocio Detectada:** {business_error}")
    print("\n**Pasos para reproducir:**")
    print(f"1. Enviar petición HTTP {method} a la ruta `{endpoint}`.")
    print("2. Configurar los encabezados correspondientes (ej. `Content-Type: application/json`).")
    if payload is not None:
        print(f"3. Enviar el siguiente cuerpo de solicitud (Payload):\n```json\n{json.dumps(payload, indent=4)}\n```")
    print(f"\n**Resultado Esperado:** Código HTTP {expected_status} con la validación de negocio correspondiente.")
    print(f"**Resultado Actual:** Código HTTP {actual_status}.\nCuerpo de la respuesta:\n```json\n{response_body}\n```")
    print("=" * 70 + "\n")

def run_tests():
    file_path = os.path.join("Data", "delivery_cases.json")
    if not os.path.exists(file_path):
        print(f"❌ No se encontró el archivo de datos en {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        test_suite = json.load(f)

    results_data = []
    failed_tests = 0
    passed_tests = 0

    print(f"\n🚀 Iniciando ejecución automatizada de {len(test_suite)} casos de prueba con validación de negocio...")
    print("=" * 70)

    for case in test_suite:
        url = f"{BASE_URL}{case['endpoint']}"
        method = case['method']
        headers = case['headers']
        payload = case['payload']
        expected_status = case['expected_status']
        expected_is_possible = case.get('expected_is_possible')
        
        try:
            if method == "POST":
                if headers.get("Content-Type") == "text/plain" and isinstance(payload, dict):
                    response = requests.post(url, data=json.dumps(payload), headers=headers)
                else:
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

            # Validaciones combinadas: HTTP + Regla de Negocio (isItPossibleToDeliver)
            http_matched = (actual_status == expected_status)
            business_matched = True
            business_error_msg = ""

            is_possible = resp_body.get("isItPossibleToDeliver") if isinstance(resp_body, dict) else None

            if http_matched and actual_status == 200 and expected_is_possible is not None:
                if is_possible != expected_is_possible:
                    business_matched = False
                    business_error_msg = f"Se esperaba 'isItPossibleToDeliver: {expected_is_possible}' según la regla de negocio, pero la API devolvió '{is_possible}'."

            status_matched = http_matched and business_matched
            
            if status_matched:
                passed_tests += 1
                status_label = "Passed"
                if actual_status == 200:
                    if is_possible is True:
                        actual_result_text = "El sistema procesó la solicitud devolviendo HTTP 200 OK y confirmando entrega viable (isItPossibleToDeliver: true)."
                    elif is_possible is False:
                        actual_result_text = "El sistema procesó la consulta devolviendo HTTP 200 OK y determinó correctamente que la entrega no es viable (isItPossibleToDeliver: false)."
                    else:
                        actual_result_text = "El sistema procesó la solicitud correctamente devolviendo HTTP 200 OK."
                elif actual_status == 405:
                    actual_result_text = "El sistema rechazó el método no permitido respondiendo correctamente con HTTP 405 Method Not Allowed."
                else:
                    actual_result_text = f"El sistema respondió con el código esperado HTTP {actual_status}."
            else:
                failed_tests += 1
                status_label = "Failed"
                if http_matched and not business_matched:
                    actual_result_text = f"El sistema devolvió HTTP 200 OK pero violó la regla de negocio: se esperaba 'isItPossibleToDeliver: {expected_is_possible}', pero obtuvo '{is_possible}'."
                elif expected_status == 415 and actual_status == 200:
                    actual_result_text = f"El sistema aceptó la cabecera 'Content-Type: {headers.get('Content-Type')}' devolviendo HTTP 200 OK en lugar de rechazar con HTTP 415 o 400."
                else:
                    actual_result_text = f"El sistema devolvió HTTP {actual_status} OK procesando la solicitud, en lugar de rechazarla con el código esperado HTTP {expected_status} Bad Request."

            results_data.append({
                "ID": case['id'],
                "Nombre": case['name'],
                "Estatus": status_label,
                "Estado Esperado": expected_status,
                "Estado Obtenido": actual_status,
                "Resultado Obtenido Redactado": actual_result_text
            })

            print(f"  [{status_label.upper()}] Caso #{case['id']}: {case['name']}")
            print(f"     └─ Resultado Obtenido: {actual_result_text}\n")

            if not status_matched:
                generate_jira_bug_report(
                    test_id=case['id'],
                    test_name=case['name'],
                    endpoint=case['endpoint'],
                    method=method,
                    payload=payload,
                    expected_status=expected_status,
                    actual_status=actual_status,
                    response_body=resp_text,
                    business_error=business_error_msg
                )

        except requests.exceptions.RequestException as e:
            failed_tests += 1
            print(f"  [ERROR] Caso #{case['id']} falló por excepción de red: {e}\n")

    print("=" * 70)
    print(f"📊 RESUMEN FINAL: {passed_tests} PASSED, {failed_tests} FAILED (bugs técnicos o de negocio detectados).")
    print("=" * 70 + "\n")

    os.makedirs("Artifacts/Reports", exist_ok=True)
    csv_path = os.path.join("Artifacts", "Reports", "delivery_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["ID", "Nombre", "Estatus", "Estado Esperado", "Estado Obtenido", "Resultado Obtenido Redactado"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_data)

    print(f"📁 Reporte CSV exportado con éxito a: {csv_path}")

    del test_suite
    del results_data

if __name__ == "__main__":
    run_tests()
