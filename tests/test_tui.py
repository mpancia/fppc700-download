from textual.widgets import Footer, Header

from fppc700download.tui.app import FppcApp


async def test_app_mounts_header_and_footer():
    app = FppcApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(Header) is not None
        assert app.query_one(Footer) is not None
