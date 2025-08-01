import requests
import json

# Test the tax game API endpoint
def test_tax_game_api():
    url = "http://127.0.0.1:8000/generate-tax-game"
    
    test_data = {
        "message": "I'm a software engineer earning 12 LPA, want to save maximum tax while building wealth for house purchase"
    }
    
    print("Testing Tax Game API...")
    print(f"URL: {url}")
    print(f"Request: {test_data}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received successfully!")
            print(f"Monthly Incomes: {data.get('monthlyIncomes', {})}")
            print(f"Number of months with options: {len(data.get('monthlyOptions', {}))}")
            
            # Check if we have options for month 1
            if '1' in data.get('monthlyOptions', {}):
                month1_options = data['monthlyOptions']['1']
                print(f"Month 1 - High options: {len(month1_options.get('high', []))}")
                print(f"Month 1 - Medium options: {len(month1_options.get('medium', []))}")
                print(f"Month 1 - Low options: {len(month1_options.get('low', []))}")
                
                # Show first high option to check if it's default or custom
                if month1_options.get('high'):
                    first_option = month1_options['high'][0]
                    print(f"First high option: {first_option}")
                    
                    # Check if this looks like default data
                    if first_option.get('label') == 'ELSS Mutual Funds' and first_option.get('amount') == 50000:
                        print("⚠️  This appears to be DEFAULT data - Gemini API may not be working")
                    else:
                        print("🎯 This appears to be CUSTOM data from Gemini API!")
                        
            # Check if all months have the same data (indicating defaults)
            all_months_data = data.get('monthlyOptions', {})
            if len(all_months_data) >= 2:
                month1_data = all_months_data.get('1', {})
                month2_data = all_months_data.get('2', {})
                if month1_data == month2_data:
                    print("⚠️  All months have identical data - likely using defaults")
                else:
                    print("✅ Months have different data - API is working!")
                        
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_tax_game_api()
