import json
import logging
from quart import Quart, request, jsonify
from quart_cors import cors
from uagents.query import query
from uagents import Model

app = Quart(__name__)
app = cors(app, allow_origin="http://localhost:5173")

# Update with your job agent's address
job_agent_address = 'agent1qgjwsfkyhx4pgmnfnaqa7vacjrnua0wlh62q7tzf476g8lle660pjg0sm06'

# Define the job request model


class JobRequest(Model):
    job_description: str

# Define the job response model


class JobResponse(Model):
    jobs: list

# Define the error response model


class ErrorResponse(Model):
    error: str


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/api/jobs/', methods=['POST'])
async def get_jobs():
    try:
        data = await request.json
        description = data.get('description', '')
        if not description:
            return jsonify({'error': 'Job description is required'}), 400

        # Query the job agent
        logger.info("Sending query to agent with description: %s", description)
        response = await query(destination=job_agent_address, message=JobRequest(job_description=description), timeout=240.0)

        response = json.loads(response.decode_payload())

        if response is None:
            raise ValueError("Received no response from the agent")

        # Extract job details from agent response
        logger.info("Received response from agent: %s", response)

        if isinstance(response, dict) and 'error' in response:
            raise ValueError(response['error'])

        return jsonify(response['jobs'])

    except Exception as e:
        logger.error("Error occurred: %s", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


