"""
Compatibility shim for imghdr module (removed in Python 3.13)
"""
import sys

# Create a minimal imghdr module for tweepy compatibility
class ImghdrCompat:
    @staticmethod
    def what(file, h=None):
        """Minimal implementation - just returns 'jpeg' for any image"""
        return 'jpeg'

# Install the compatibility module
sys.modules['imghdr'] = ImghdrCompat()
