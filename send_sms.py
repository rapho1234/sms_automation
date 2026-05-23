from datetime import timedelta, date, datetime
import requests
import mysql.connector
import keys_sms

API_KEY = keys_sms.API_KEY
PARTNER_ID = keys_sms.PARTNER_ID
SHORTCODE = keys_sms.SHORTCODE
host_address = keys_sms.HOST_ADDRESS
dbms_user = keys_sms.DBMS_USER
pass_dkey = keys_sms.DBMS_PASS
database = keys_sms.DATABASE

# Database connection object
mydb = mysql.connector.connect(
    host=host_address,
    user=dbms_user,
    password=pass_dkey,
    database=database,
    use_pure=True
)

def get_client_ids(mydb):
    with mydb.cursor() as cursor:
        cursor.callproc('GetClientId')
        results = [result.fetchall() for result in cursor.stored_results()]
        my_list = [item for sublist in results for item in sublist]
        flat_list = [x[0] for x in my_list]
        print(flat_list)  # Output: [77, 121, 136]
        return flat_list

def get_phone_numbers():
    mycursor = mydb.cursor(dictionary=True)

    # Matches exactly 2 days from today
    sql_query = """
        SELECT
            c.first_name,
            c.mobile_number,
            u.account_details
        FROM clients_clients c
        JOIN clients_clientusagebundle u ON c.id = u.client_id
        WHERE u.status = 1
          AND DATE(u.end_date) = DATE_ADD(CURDATE(), INTERVAL 2 DAY);
    """

    try:
        mycursor.execute(sql_query)
        results = mycursor.fetchall()

        if not results:
            print("📭 No accounts are expiring 2 days from now.")
            return

        for row in results:
            client_name = row['first_name']
            client_number = row['mobile_number']
            client_account = row['account_details']

            print(f"Expiring soon: {client_name} | {client_number} | Account: {client_account}")
            send_text(client_name, client_number, client_account)

    except Exception as e:
        print(f"❌ Database error: {e}")

    finally:
        mycursor.close()

# -------------------------------
# FORMAT PHONE NUMBER
# -------------------------------
def format_phone_number(phone):
    phone = str(phone).strip()

    if phone.startswith("0"):
        return "254" + phone[1:]
    elif phone.startswith("+254"):
        return phone[1:]
    elif phone.startswith("254"):
        return phone
    else:
        return phone

# -------------------------------
# SEND SMS
# -------------------------------
def send_text(customer, tel_no, account_number):
    # ✅ CORRECTED ENDPOINT (Do not change this back to textsms.co.ke)
    url = "https://sms.textsms.co.ke/api/services/sendsms/"

    formatted_phone = format_phone_number(tel_no)

    end_date = date.today() + timedelta(days=2)
    expiry_date = end_date.strftime("%d/%m/%Y")

    message = (
        f"FROM: YOUR SENDER ID. Dear {customer}, "
        f"Your fiber internet expires on {expiry_date}. "
        f"Please renew via Mpesa Paybill No: XXXX." # you unique payment gateway
        f"Account No: {account_number}. Thank you."
    )

    payload = {
        "apikey": API_KEY,
        "partnerID": PARTNER_ID,
        "message": message,
        "shortcode": SHORTCODE,
        "mobile": formatted_phone
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        # ✅ Validate that the response is JSON to prevent crashing on HTML errors
        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()

            print(f"\n📨 Response for {formatted_phone}:")
            print(data)

            if "responses" in data:
                for res in data["responses"]:
                    # TextSMS sometimes has a typo in their dictionary keys
                    code = res.get("response-code") or res.get("respose-code")

                    if str(code) == "200":
                        print(f"✅ SMS sent successfully to {formatted_phone}")
                        msg_id = res.get("messageid")
                        print(f"📌 Message ID: {msg_id}")
                    else:
                        print(f"❌ Failed: {res.get('response-description')}")
            else:
                print("❌ Unexpected JSON structure received from API.")
        else:
            print(f"❌ API Error: TextSMS returned an HTML page instead of JSON.")
            print(f"Status Code: {response.status_code}")

    except Exception as e:
        print(f"❌ Error sending SMS: {e}")

# -------------------------------
# MAIN EXECUTION
# -------------------------------
def main():
    print(f"--- Script started at {datetime.now()} ---")
    get_phone_numbers()
    print("--- Script finished ---")

if __name__ == "__main__":
    main()
