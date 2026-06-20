import unittest
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from protego.nlp.preprocess import clean_text
from protego.logic.rag_engine import query_kb
import protego.logic.db_helper as db
from protego.api.chatbot_service import handle_message
from protego.logic.context_memory import ContextMemory

class TestProtegoLogic(unittest.TestCase):
    
    def setUp(self):
        # Override database path to isolate unit tests
        self.test_db_path = Path(__file__).resolve().parent / "protego_test.db"
        db.DB_PATH = self.test_db_path
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass
        db.init_local_db()
        
    def tearDown(self):
        # Clean up test database file
        if hasattr(self, "test_db_path") and self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass
        
    def test_text_cleaning(self):
        # Test basic text clean (retains exclamation marks for safety indicators)
        self.assertEqual(clean_text("Hello World!!!"), "hello world!!")
        # Test repeat char normalization
        self.assertEqual(clean_text("sooooo stressed"), "soo stressed")
        # Test URL removal (short messages <= 3 words skip stopword removal)
        self.assertEqual(clean_text("help me at http://google.com"), "help me at")
        # Test negation preservation
        self.assertIn("not", clean_text("I do not feel safe"))
        
    def test_db_operations(self):
        user_id = "test_user_99"
        # Test add user
        db.add_user(user_id, "Test User", "test@protego.org")
        users = db.get_users()
        user_ids = [u["id"] for u in users]
        self.assertIn(user_id, user_ids)
        
        # Test save and get chat
        success_chat = db.save_chat(user_id, "Hello chatbot", "Hi user", "low")
        self.assertTrue(success_chat)
        chats = db.get_chats()
        latest_chat = chats[0]
        self.assertEqual(latest_chat["user_id"], user_id)
        self.assertEqual(latest_chat["message"], "Hello chatbot")
        self.assertEqual(latest_chat["response"], "Hi user")
        
        # Test save and get location
        success_loc = db.save_location(user_id, 12.34, 56.78)
        self.assertTrue(success_loc)
        locs = db.get_locations()
        self.assertTrue(len(locs) > 0)
        self.assertEqual(locs[0]["user_id"], user_id)
        
        # Test save and get safety plan
        success_plan = db.save_safety_plan(
            user_id, "Contact1", "EarlySigns1", "SafePlace1", "Steps1", "Pack1", "CODEWORD"
        )
        self.assertTrue(success_plan)
        plan = db.get_safety_plan(user_id)
        self.assertEqual(plan["safe_contacts"], "Contact1")
        self.assertEqual(plan["code_word"], "CODEWORD")

    def test_rag_query(self):
        # Test query matches
        matches = query_kb("secure phone location GPS", top_k=1, min_score=0.01)
        self.assertTrue(len(matches) > 0)
        self.assertIn("location", matches[0]["content"].lower() or matches[0]["title"].lower())
        
    def test_chatbot_service(self):
        # Test low risk response
        res_low = handle_message("Hello, how are you today?", country="India")
        self.assertEqual(res_low["risk_level"], "low")
        self.assertFalse(res_low["show_emergency"])
        
        # Test high risk response
        res_high = handle_message("He threatened to hit me and is locking the doors", country="United States")
        self.assertTrue(res_high["risk_level"] in ["high", "emergency"])

if __name__ == "__main__":
    unittest.main()
