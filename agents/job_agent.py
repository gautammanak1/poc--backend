import requests
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Define the job request model


class JobRequest(Model):
    job_description: str

# Define the response model


class JobResponse(Model):
    jobs: list

# Define the error response model


class ErrorResponse(Model):
    error: str

# Function to get job details from the external API


async def get_job_details(job_role):
    url = "https://indeed11.p.rapidapi.com/"
    payload = {
        "search_terms": job_role,
        "location": "United States",
        "page": "1"
    }
    headers = {
        # Replace with your key
        'x-rapidapi-key': "f305d729f7msh392708bf2c11363p1dcb9cjsn26021afb9318", 
        'x-rapidapi-host': "indeed11.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

# Define the JobAgent
JobAgent = Agent(
    name="JobAgent",
    port=8002,
    seed="Job Agent secret phrase",
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Register agent on Almanac and fund it if necessary
fund_agent_if_low(JobAgent.wallet.address())

# On agent startup, print the address


@JobAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'Job Agent Address is {JobAgent.address}')

# Define the handler for job requests


@JobAgent.on_query(model=JobRequest, replies={JobResponse, ErrorResponse})
async def query_handler(ctx: Context, sender: str, msg: JobRequest):
    try:
        ctx.logger.info(f"Received job request: {msg.job_description}")
        details = await get_job_details(msg.job_description)
        if 'error' in details:
            raise Exception(details['message'])

        # Prepare jobs response
        jobs = []
        for detail in details:
            job_title = detail.get('job_title', 'No title available')
            company_name = detail.get('company_name', 'No company name available')
            location = detail.get('location', 'No location available')
            salary = detail.get('salary', 'No salary information available')
            summary = detail.get('summary', 'No summary available')
            job_date = detail.get('date', 'Just posted')
            job_url = detail.get('url', 'No URL available')

            job_data = {
                "title": job_title,
                "company": company_name,
                "location": location,
                "salary": salary,
                "summary": summary,
                "date": job_date,
                "url": job_url
            }
            jobs.append(job_data)

        ctx.logger.info(f"Job details sent for {msg.job_description}: {jobs}")
        await ctx.send(sender, JobResponse(jobs=jobs))

    except Exception as e:
        error_message = f"An error occurred while fetching job details: {e}"
        ctx.logger.error(error_message)
        # Ensure error message is a string
        await ctx.send(sender, ErrorResponse(error=str(error_message)))

# Starting agent
if __name__ == "__main__":
    JobAgent.run()
