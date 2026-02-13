"""Application entry point for launching the GUI."""

from controller.flow_controller import flow_controller


if __name__ == "__main__":
    flow_controller().run()
