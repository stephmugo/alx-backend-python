#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Entry point for Django management commands.
    
    - Sets the default settings module for the project.
    - Executes commands like runserver, migrate, makemigrations, etc.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_signals_project.settings')

    try:
        # Import the management utility to handle command-line arguments.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Provide a helpful error message if Django isn't installed or activated.
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and "
            "that your virtual environment is activated."
        ) from exc

    # Run the appropriate Django command passed from the command line.
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
