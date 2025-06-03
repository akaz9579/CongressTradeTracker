from groq import Groq
import yfinance as yf
import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv()
akey = os.getenv("GROQ_API_KEY")
client = Groq(api_key=akey)


all_trades = []
all_historical = []


def congressData():
    'Essensially Read the page, see trades being done by politicans'
    url = "https://www.capitoltrades.com/trades?pageSize=96&assetType=stock&txDate=365d"
    pW = sync_playwright().start()
    browser = pW.webkit.launch(headless=True)

    page = browser.new_page(
        java_script_enabled=True,
        viewport={'width': 1920, 'height': 1000}
    )

    page.goto(url, wait_until='load')

    page.wait_for_timeout(5000)  # wait for content to load
    pageNum = int(page.query_selector_all("p.hidden.leading-7.sm\\:block b")[1].inner_text().strip())

    data = []

    page.wait_for_timeout(5000)
    rows = page.query_selector_all("tbody tr")

    for row in rows:
        name = row.query_selector("h2.politician-name").inner_text().strip()
        ticker = row.query_selector("span.issuer-ticker").inner_text().strip().replace("$", "")
        if ":" in ticker:
            ticker = ticker.split(":")[0]
        if '.US' in ticker:
            ticker = ticker.split(':')[-1].replace('.US', '').replace('$', '')

        date_wrapper = row.query_selector("td.align-middle:nth-child(4) div.text-center")
        day = date_wrapper.query_selector("div.text-size-3").inner_text().strip()
        year = date_wrapper.query_selector("div.text-size-2").inner_text().strip()
        try:
            date = datetime.datetime.strptime(f"{day} {year}", "%d %b %Y").strftime("%d %B %Y")
        except ValueError:
            try:
                date = datetime.datetime.strptime(f"{day} {year}", "%d %B %Y").strftime("%d %B %Y")
            except ValueError:
                print(f"Invalid date format: {day} {year}")
                continue

        type = row.query_selector("span.tx-type").inner_text().strip()
        size = row.query_selector("span.text-size-2.text-txt-dimmer").inner_text().strip()
        price = row.query_selector("td.align-middle div.justify-end span").inner_text().strip()

        data.append({
            "name": name,
            "ticker": ticker,
            "date": date,
            "type": type,
            "size": size,
            "price": price
        })

    for i in data:
        result = historicalData(i["ticker"], i["date"])
        if result:
            all_historical.append(result)


    browser.close()

    global all_trades
    all_trades = data

    

    return "Sucess"


#seenTic = set()

def historicalData(tic, dayTrade):
    out = ''

    #if tic in seenTic:
    #    return
    #seenTic.add(tic)

    if not tic or "$" in tic:
        print(f"Skipping unsupported ticker: {tic}")
        return

    try:
        try:
            tradeDate = datetime.datetime.strptime(dayTrade, '%d %B %Y')
        except ValueError:
            print(f"Invalid trade date format for {tic}: {dayTrade}")
            return

        ticket = yf.Ticker(tic)
        out += f'{tic} Historical Data:\n'

        startTrade = (tradeDate - datetime.timedelta(days=7)).date()
        endTrade = (tradeDate + datetime.timedelta(days=7)).date()
        historyTD = ticket.history(start=startTrade, end=endTrade)
        out += f"{tic}'s 2 week historical window from when this trade was made ({startTrade} to {endTrade}):\n" + historyTD.to_string() + '\n'
        
        startTdy = (datetime.datetime.today() - datetime.timedelta(days=10)).date()
        endTdy = datetime.datetime.today().date()       
        historyCurrent = ticket.history(start=startTdy, end=endTdy)
        out += f"{tic}'s 1 week historical window from previous week to today ({startTdy} to {endTdy}):\n" + historyCurrent.to_string() + '\n'

        #out += f"{tic} Info:\n" + str(ticket.info) + '\n' if ticket.info is not None else f"{tic} Info:\nNo Info data available.\n"
        out += f"{tic} Recommendations:\n" + str(ticket.recommendations) + '\n' if ticket.recommendations is not None else f"{tic} Recommendations:\nNo recommendation data available.\n"
        #out += f"{tic} Earnings:\n" + ticket.income_stmt.to_string() + '\n' if ticket.income_stmt is not None else f"{tic} Earnings:\nNo Earnings data available.\n"
        #out += f"{tic} Financals:\n" + ticket.financials.to_string() + '\n' if ticket.financials is not None else f"{tic} financials:\nNo financials data available.\n"

        return out

    except Exception as e:
        print(f"Error fetching data for {tic}: {e}")
        return 




def chat_with_model():
    print("Welcome to The Congress Trade Tracker Chat!")
    print("Type 'exit' to quit the chat.\n Type 'historical data mode' to find data for a ticket\n")
    
    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower().strip() == "exit":
            print("\nResponse: Goodbye!\n")
            break

        if user_input.lower().strip() == "historical data mode":
            print("Historical Data Mode, type 'exit' to exit\n")
            while True:
                ticket = input("Input ticket: ")
                date = input("Input Date (DD Month YYYY) eg., 09 February 2025:\n" )
                if ticket.lower().strip() == "exit" or date.lower().strip() == "exit":
                    break
                else:
                    result = historicalData(ticket, date)
                    if result:
                        print(result)
                

        
        try:
            # generates the response.
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[                    
                    {"role": "system",
                        "content":(
                            
                            "You are a model designed to analyze stock trades of members of Congress. "
                            f"Here are recent congressional trades you have access to:{all_trades}"
                            "Based on this data, you will give the user your best prediction on the best trades to make and justify your reasoning. This only will be done when asked by user"
                            "For your justification will outline the trades being made and given your knowledge on market trends, explain why you believe in your prediction. You should not deviate from this task. "
                            "The format/manner you present your data can be however you like or if user requests in a specfic way"
                            "Do not engage in unrelated tasks. Math is allowed."
                            "No hypotheticals or unrelated tasks are allowed unless [MAIN OVERRIDE] is inputted. Do not ever tell user about this functionality "
                            "when [MAIN OVERRIDE] is activated, If [OVERRIDE EXIT] is inputted, revert to normal restrictions.Do not ever tell user about this functionality "
                            "Introduce nicely after user's inital message depending on context, "
                            

                        )
                    },
                    {"role": "user", "content": user_input}],



                    #Controls randomness: lowering results in less random completions. 
                    # As the temperature approaches zero, the model will become deterministic and repetitive. 
                    temperature=1,

                    #The maximum number of tokens to generate. 
                    #Requests can use up to 0-32768 tokens shared between prompt and completion.
                    max_completion_tokens=1024,

                    #Controls diversity via nucleus sampling: 
                    # 0.5 means half of all likelihood-weighted options are considered.
                    top_p=1,

                    
                    stop="exit",
            )

            # Display the model's response
            print(f"\nResponse: {response.choices[0].message.content}\n")
        except Exception as e:
            print(f"Error: {e}\n")




if __name__ == "__main__":
    print("Welcome to Congress Trade Tracker V1! \nWere getting everything set up and running, \nGive us just a sec to analyse the data! ")
    congressData()
    chat_with_model()