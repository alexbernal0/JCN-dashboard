"""
Comprehensive Error Handler for JCN Dashboard
Provides detailed error messages and diagnostics for easier debugging
"""

import streamlit as st
import traceback
import sys
from datetime import datetime

def show_error_details(error, context=""):
    """Display comprehensive error information in Streamlit"""
    
    st.error(f"🚨 **Error Occurred**: {type(error).__name__}")
    
    # Error message
    st.markdown(f"**Error Message:** `{str(error)}`")
    
    # Context information
    if context:
        st.markdown(f"**Context:** {context}")
    
    # Timestamp
    st.markdown(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Full traceback in expander
    with st.expander("🔍 **Show Full Error Details** (for debugging)", expanded=False):
        st.code(traceback.format_exc(), language="python")
        
        # Python version
        st.markdown(f"**Python Version:** {sys.version}")
        
        # Helpful tips
        st.markdown("### 💡 Debugging Tips:")
        st.markdown("""
        1. **Check the error type** - tells you what went wrong
        2. **Read the error message** - often contains the specific issue
        3. **Look at the traceback** - shows where in the code the error occurred
        4. **Check line numbers** - helps locate the problematic code
        5. **Verify dependencies** - ensure all required packages are installed
        """)
    
    # Report button
    st.markdown("---")
    st.markdown("**Need help?** Copy the error details above and report the issue.")

def safe_execute(func, context="", show_success=False):
    """
    Safely execute a function with comprehensive error handling
    
    Args:
        func: Function to execute
        context: Description of what's being executed
        show_success: Whether to show success message
    
    Returns:
        Result of func() or None if error occurred
    """
    try:
        result = func()
        if show_success:
            st.success(f"✅ {context} completed successfully")
        return result
    except Exception as e:
        show_error_details(e, context)
        return None

def page_wrapper(page_func):
    """
    Decorator to wrap entire page with error handling
    
    Usage:
        @page_wrapper
        def my_page():
            # page code here
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            return page_func(*args, **kwargs)
        except Exception as e:
            st.error("🚨 **Page Error**")
            show_error_details(e, f"Loading page: {page_func.__name__}")
            
            # Offer to reload
            if st.button("🔄 Reload Page"):
                st.rerun()
    
    return wrapper
