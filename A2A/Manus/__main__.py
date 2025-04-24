from A2A.common.server import A2AServer
from A2A.common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from A2A.common.utils.push_notification_auth import PushNotificationSenderAuth
from A2A.Manus.task_manager import AgentTaskManager
from A2A.Manus.agent import ManusAgent
from app.tool.browser_use_tool import _BROWSER_DESCRIPTION
from app.tool.str_replace_editor import _STR_REPLACE_EDITOR_DESCRIPTION
from app.tool.terminate import _TERMINATE_DESCRIPTION
import click
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10000)
def main(host, port):
    """Starts the Manus Agent server."""
    try:
        capabilities = AgentCapabilities(streamiMng=False, pushNotifications=True)
        Python_execute_skill = AgentSkill(
            id="Python Execute",
            name="Python Execute Tool",
            description="Executes Python code string. Note: Only print outputs are visible, function return values are not captured. Use print statements to see results.",
            tags=["Execute Python Code"],
            examples=["Execute Python code:'''python \n Print('Hello World') \n '''"],
        )
        Browser_use_skill = AgentSkill(
            id="Browser use",
            name="Browser use Tool",
            description=_BROWSER_DESCRIPTION,
            tags=["Use Browser"],
            examples=["go_to 'https://www.google.com'"],
        )
        Str_replace_skill = AgentSkill(
            id="Replace String",
            name="Str_replace Tool",
            description=_STR_REPLACE_EDITOR_DESCRIPTION,
            tags=["Operate Files"],
            examples=["Replace 'old' with 'new' in 'file.txt'"],
        )
        Ask_human_skill = AgentSkill(
            id="Ask human",
            name="Ask human Tool",
            description="Use this tool to ask human for help.",
            tags=["Ask human for help"],
            examples=["Ask human: 'What time is it?'"],
        )
        Terminate_skill = AgentSkill(
            id="terminate",
            name="terminate Tool",
            description=_TERMINATE_DESCRIPTION,
            tags=["terminate task"],
            examples=["terminate"],
        )
        agent_card = AgentCard(
            name="Manus Agent",
            description="A versatile agent that can solve various tasks using multiple tools including MCP-based tools",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=ManusAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=ManusAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[Python_execute_skill,Browser_use_skill,Str_replace_skill,Ask_human_skill,Terminate_skill],
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=ManusAgent(), notification_sender_auth=notification_sender_auth),
            host=host,
            port=port,
        )

        server.app.add_route(
            "/.well-known/jwks.json", notification_sender_auth.handle_jwks_endpoint, methods=["GET"]
        )

        logger.info(f"Starting server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
