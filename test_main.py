import unittest
from unittest.mock import patch, call
import main

class TestConversationManagement(unittest.TestCase):

    def setUp(self):
        # Reset is_conversation_active before each test
        main.is_conversation_active = False

    @patch('main.save_conversation')
    @patch('main.call_gemini')
    @patch('builtins.print')
    @patch('builtins.input')
    def test_start_new_chat_no_active_conversation(self, mock_input, mock_print, mock_call_gemini, mock_save_conversation):
        # Setup: main.is_conversation_active is already False due to setUp
        mock_input.side_effect = ["Hello", "salir"]
        mock_call_gemini.return_value = "Gemini says hello"

        main.start_new_chat()

        # Assertions
        mock_print.assert_any_call("\n--- Nuevo Chat con Gemini (Escribe 'salir' para terminar) ---\n")
        mock_input.assert_any_call("Tú: ")
        mock_call_gemini.assert_called_once_with("Hello")
        mock_save_conversation.assert_called_once_with("Hello", "Gemini says hello")
        mock_print.assert_any_call("\n🔍 Respuesta generada por Gemini:\nGemini says hello\n")
        mock_print.assert_any_call("Volviendo al menú principal...")
        self.assertFalse(main.is_conversation_active, "is_conversation_active should be False after chat ends")

    @patch('main.save_conversation')
    @patch('main.call_gemini')
    @patch('builtins.print')
    @patch('builtins.input')
    def test_start_new_chat_active_conversation_choose_new(self, mock_input, mock_print, mock_call_gemini, mock_save_conversation):
        main.is_conversation_active = True # Setup
        mock_input.side_effect = ["1", "New chat", "salir"] # "1" to start new, then new prompt, then exit
        mock_call_gemini.return_value = "Gemini says new"

        main.start_new_chat()

        # Assertions
        mock_print.assert_any_call("Ya hay una conversación en curso.")
        mock_print.assert_any_call("Selecciona una opción:")
        mock_print.assert_any_call("1. Iniciar una nueva conversación (finalizará la actual)")
        mock_print.assert_any_call("2. Volver al menú principal")
        mock_input.assert_any_call("Opción: ") # Prompt for 1 or 2

        mock_print.assert_any_call("\n--- Nuevo Chat con Gemini (Escribe 'salir' para terminar) ---\n")
        mock_input.assert_any_call("Tú: ") # Prompt for new chat input
        mock_call_gemini.assert_called_once_with("New chat")
        mock_save_conversation.assert_called_once_with("New chat", "Gemini says new")
        mock_print.assert_any_call("\n🔍 Respuesta generada por Gemini:\nGemini says new\n")
        mock_print.assert_any_call("Volviendo al menú principal...")
        self.assertFalse(main.is_conversation_active, "is_conversation_active should be False after chat ends")

    @patch('main.save_conversation')
    @patch('main.call_gemini')
    @patch('builtins.print')
    @patch('builtins.input')
    def test_start_new_chat_active_conversation_choose_menu(self, mock_input, mock_print, mock_call_gemini, mock_save_conversation):
        main.is_conversation_active = True # Setup
        mock_input.side_effect = ["2"] # "2" to return to menu

        main.start_new_chat()

        # Assertions
        mock_print.assert_any_call("Ya hay una conversación en curso.")
        mock_print.assert_any_call("Selecciona una opción:")
        mock_print.assert_any_call("1. Iniciar una nueva conversación (finalizará la actual)")
        mock_print.assert_any_call("2. Volver al menú principal")
        mock_input.assert_any_call("Opción: ")
        mock_print.assert_any_call("Volviendo al menú principal...") # This is from the choice '2'

        self.assertTrue(main.is_conversation_active, "is_conversation_active should remain True")
        mock_call_gemini.assert_not_called()
        mock_save_conversation.assert_not_called()

    @patch('builtins.print')
    def test_finalize_conversation_when_active(self, mock_print):
        main.is_conversation_active = True # Setup

        main.finalize_conversation()

        # Assertions
        self.assertFalse(main.is_conversation_active, "is_conversation_active should be False")
        mock_print.assert_called_once_with("Conversación actual finalizada.")

    @patch('builtins.print')
    def test_finalize_conversation_when_not_active(self, mock_print):
        main.is_conversation_active = False # Setup (already false by setUp, but explicit for clarity)

        main.finalize_conversation()

        # Assertions
        self.assertFalse(main.is_conversation_active, "is_conversation_active should remain False")
        mock_print.assert_called_once_with("No hay ninguna conversación activa para finalizar.")

if __name__ == '__main__':
    unittest.main()
