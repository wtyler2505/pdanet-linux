#!/usr/bin/env python3
"""
PdaNet Linux GUI - Badass GTK interface for PdaNet tethering
"""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
import subprocess
import threading
import time

from gi.repository import AppIndicator3, Gdk, GLib, Gtk


class PdaNetGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="PdaNet Linux")
        self.set_default_size(500, 400)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)

        # State
        self.connected = False
        self.stealth_enabled = False
        self.checking_status = False

        # Apply dark theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        # Load custom CSS for badass styling
        self.load_custom_css()

        # Setup UI
        self.setup_ui()

        # Setup system tray
        self.setup_indicator()

        # Check initial status
        GLib.timeout_add(1000, self.update_status)

    def load_custom_css(self):
        """Load custom CSS for badass appearance"""
        css = b"""
        .big-button {
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            border-radius: 8px;
        }

        .connect-button {
            background: linear-gradient(to bottom, #4CAF50, #45a049);
            color: white;
            border: 2px solid #2d7a2e;
        }

        .connect-button:hover {
            background: linear-gradient(to bottom, #5fbf63, #4CAF50);
        }

        .disconnect-button {
            background: linear-gradient(to bottom, #f44336, #da190b);
            color: white;
            border: 2px solid #a31008;
        }

        .disconnect-button:hover {
            background: linear-gradient(to bottom, #ff5449, #f44336);
        }

        .status-connected {
            color: #4CAF50;
            font-size: 24px;
            font-weight: bold;
        }

        .status-disconnected {
            color: #f44336;
            font-size: 24px;
            font-weight: bold;
        }

        .info-label {
            font-size: 14px;
            color: #aaaaaa;
        }

        .header-label {
            font-size: 28px;
            font-weight: bold;
            color: #00bcd4;
        }
        """

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def setup_ui(self):
        """Build the main UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.add(main_box)

        # Header
        header = Gtk.Label(label="⚡ PdaNet Linux ⚡")
        header.get_style_context().add_class("header-label")
        main_box.pack_start(header, False, False, 0)

        # Status section
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        status_frame = Gtk.Frame(label=" Connection Status ")
        status_frame.add(status_box)
        status_frame.set_margin_top(10)
        status_frame.set_margin_bottom(10)
        main_box.pack_start(status_frame, False, False, 0)

        # Status label
        self.status_label = Gtk.Label(label="● DISCONNECTED")
        self.status_label.get_style_context().add_class("status-disconnected")
        status_box.pack_start(self.status_label, False, False, 10)

        # Info labels
        self.interface_label = Gtk.Label(label="Interface: Not detected")
        self.interface_label.get_style_context().add_class("info-label")
        status_box.pack_start(self.interface_label, False, False, 0)

        self.proxy_label = Gtk.Label(label="Proxy: 192.168.49.1:8000")
        self.proxy_label.get_style_context().add_class("info-label")
        status_box.pack_start(self.proxy_label, False, False, 0)

        self.stealth_label = Gtk.Label(label="Stealth Mode: Disabled")
        self.stealth_label.get_style_context().add_class("info-label")
        status_box.pack_start(self.stealth_label, False, False, 0)

        # Separator
        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(separator1, False, False, 0)

        # Connect/Disconnect button
        self.main_button = Gtk.Button(label="CONNECT")
        self.main_button.get_style_context().add_class("big-button")
        self.main_button.get_style_context().add_class("connect-button")
        self.main_button.connect("clicked", self.on_main_button_clicked)
        self.main_button.set_size_request(-1, 80)
        main_box.pack_start(self.main_button, False, False, 0)

        # Stealth mode toggle
        stealth_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        stealth_box.set_halign(Gtk.Align.CENTER)

        stealth_label = Gtk.Label(label="Stealth Mode (Hide Tethering):")
        stealth_box.pack_start(stealth_label, False, False, 0)

        self.stealth_switch = Gtk.Switch()
        self.stealth_switch.connect("notify::active", self.on_stealth_toggled)
        stealth_box.pack_start(self.stealth_switch, False, False, 0)

        main_box.pack_start(stealth_box, False, False, 0)

        # Separator
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(separator2, False, False, 0)

        # Bottom buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_homogeneous(True)

        about_btn = Gtk.Button(label="About")
        about_btn.connect("clicked", self.show_about)
        button_box.pack_start(about_btn, True, True, 0)

        quit_btn = Gtk.Button(label="❌ Quit")
        quit_btn.connect("clicked", self.on_quit)
        button_box.pack_start(quit_btn, True, True, 0)

        main_box.pack_start(button_box, False, False, 0)

    def setup_indicator(self):
        """Setup system tray indicator"""
        self.indicator = AppIndicator3.Indicator.new(
            "pdanet-linux", "network-wireless", AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("PdaNet Linux")

        # Create menu
        menu = Gtk.Menu()

        # Show window
        show_item = Gtk.MenuItem(label="Show Window")
        show_item.connect("activate", lambda x: self.present())
        menu.append(show_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Quick connect/disconnect
        self.tray_action_item = Gtk.MenuItem(label="Connect")
        self.tray_action_item.connect("activate", self.on_tray_action)
        menu.append(self.tray_action_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        menu.append(quit_item)

        menu.show_all()
        self.indicator.set_menu(menu)

    def update_status(self):
        """Update connection status"""
        if self.checking_status:
            return True

        self.checking_status = True

        def check():
            try:
                # Check if redsocks is running
                result = subprocess.run(
                    ["systemctl", "is-active", "redsocks"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                is_connected = result.stdout.strip() == "active"

                # Check stealth mode
                result = subprocess.run(
                    ["sudo", "-n", "iptables", "-t", "mangle", "-L", "PDANET_STEALTH"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                is_stealth = result.returncode == 0

                # Check interface
                result = subprocess.run(
                    ["ip", "link", "show"], check=False, capture_output=True, text=True
                )
                interface = "Not detected"
                for line in result.stdout.split("\n"):
                    if "usb" in line or "rndis" in line:
                        interface = line.split(":")[1].strip().split("@")[0]
                        break

                GLib.idle_add(self.update_ui_state, is_connected, is_stealth, interface)
            except Exception as e:
                print(f"Status check error: {e}")
            finally:
                self.checking_status = False

        threading.Thread(target=check, daemon=True).start()
        return True

    def update_ui_state(self, is_connected, is_stealth, interface):
        """Update UI based on state"""
        self.connected = is_connected
        self.stealth_enabled = is_stealth

        if is_connected:
            self.status_label.set_markup("<span class='status-connected'>● CONNECTED</span>")
            self.main_button.set_label("DISCONNECT")
            self.main_button.get_style_context().remove_class("connect-button")
            self.main_button.get_style_context().add_class("disconnect-button")
            self.tray_action_item.set_label("Disconnect")
            self.indicator.set_icon("network-wireless-connected")
        else:
            self.status_label.set_markup("<span class='status-disconnected'>● DISCONNECTED</span>")
            self.main_button.set_label("CONNECT")
            self.main_button.get_style_context().remove_class("disconnect-button")
            self.main_button.get_style_context().add_class("connect-button")
            self.tray_action_item.set_label("Connect")
            self.indicator.set_icon("network-wireless-disconnected")

        self.interface_label.set_text(f"Interface: {interface}")
        self.stealth_label.set_text(f"Stealth Mode: {'Enabled' if is_stealth else 'Disabled'}")

        # Update stealth switch without triggering signal
        self.stealth_switch.handler_block_by_func(self.on_stealth_toggled)
        self.stealth_switch.set_active(is_stealth)
        self.stealth_switch.handler_unblock_by_func(self.on_stealth_toggled)

        return False

    def on_main_button_clicked(self, button):
        """Handle connect/disconnect button"""
        button.set_sensitive(False)

        def action():
            try:
                if self.connected:
                    # Disconnect
                    subprocess.run(
                        ["sudo", "/home/wtyler/pdanet-linux/pdanet-disconnect"], check=True
                    )
                    GLib.idle_add(
                        self.show_notification, "Disconnected", "PdaNet connection closed"
                    )
                else:
                    # Connect
                    result = subprocess.run(
                        ["sudo", "/home/wtyler/pdanet-linux/pdanet-connect"],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        GLib.idle_add(
                            self.show_notification, "Connected", "PdaNet connection established!"
                        )
                    else:
                        GLib.idle_add(self.show_error, "Connection Failed", result.stderr)
            except Exception as e:
                GLib.idle_add(self.show_error, "Error", str(e))
            finally:
                time.sleep(1)
                GLib.idle_add(self.update_status)
                GLib.idle_add(button.set_sensitive, True)

        threading.Thread(target=action, daemon=True).start()

    def on_stealth_toggled(self, switch, gparam):
        """Handle stealth mode toggle"""
        enabled = switch.get_active()

        def action():
            try:
                cmd = "enable" if enabled else "disable"
                subprocess.run(
                    ["sudo", "/home/wtyler/pdanet-linux/scripts/stealth-mode.sh", cmd], check=True
                )
                GLib.idle_add(self.update_status)
            except Exception as e:
                GLib.idle_add(self.show_error, "Stealth Mode Error", str(e))

        threading.Thread(target=action, daemon=True).start()

    def on_tray_action(self, widget):
        """Handle tray menu connect/disconnect"""
        self.on_main_button_clicked(self.main_button)

    def show_notification(self, title, message):
        """Show notification dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_error(self, title, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_about(self, button):
        """Show about dialog"""
        about = Gtk.AboutDialog(transient_for=self)
        about.set_program_name("PdaNet Linux")
        about.set_version("1.0.0")
        about.set_comments("Reverse-engineered Linux client for PdaNet USB tethering")
        about.set_website("https://github.com/yourusername/pdanet-linux")
        about.set_website_label("GitHub Repository")
        about.set_authors(["Reverse Engineered from PdaNet Windows"])
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_logo_icon_name("network-wireless")
        about.run()
        about.destroy()

    def on_quit(self, widget):
        """Quit application"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Quit PdaNet Linux?",
        )
        dialog.format_secondary_text(
            "This will close the GUI but won't disconnect active connections."
        )
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            Gtk.main_quit()


def main():
    app = PdaNetGUI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
