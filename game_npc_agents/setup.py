from setuptools import setup, find_packages

setup(
    name="game_npc_langgraph",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langgraph",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "game-npc=game_npc_langgraph.main:run_game"
        ]
    },
)
