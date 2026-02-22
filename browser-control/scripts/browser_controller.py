#!/usr/bin/env python3
"""
Browser Controller - Script para controlar navegadores vía Playwright.
Soporta: navegación, clicks, input, screenshots, extracción de datos, JavaScript, etc.
Incluye sistema de Recipes (recetas) para automatizaciones reutilizables.
"""

import argparse
import json
import base64
import sys
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

# Importaciones condicionales para manejar la falta de playwright
try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Directorio para almacenar recipes
RECIPES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes")
os.makedirs(RECIPES_DIR, exist_ok=True)


@dataclass
class ActionResult:
    """Resultado de una acción del navegador."""
    success: bool
    action: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    screenshot: Optional[str] = None  # Base64 encoded
    url: Optional[str] = None
    title: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RecipeManager:
    """Gestiona recipes (recetas) de automatización."""
    
    @staticmethod
    def get_recipe_path(name: str) -> str:
        """Obtiene la ruta del archivo de un recipe."""
        # Sanitizar nombre de archivo
        safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '-').lower()
        return os.path.join(RECIPES_DIR, f"{safe_name}.json")
    
    @staticmethod
    def create_recipe(name: str, description: str, steps: List[Dict[str, Any]], 
                      variables: Optional[Dict[str, str]] = None) -> ActionResult:
        """Crea un nuevo recipe."""
        try:
            recipe = {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "variables": variables or {},
                "steps": steps
            }
            
            recipe_path = RecipeManager.get_recipe_path(name)
            with open(recipe_path, 'w', encoding='utf-8') as f:
                json.dump(recipe, f, indent=2, ensure_ascii=False)
            
            return ActionResult(
                success=True,
                action="create_recipe",
                data={
                    "name": name,
                    "path": recipe_path,
                    "steps_count": len(steps),
                    "variables": list(recipe["variables"].keys())
                }
            )
        except Exception as e:
            return ActionResult(success=False, action="create_recipe", error=str(e))
    
    @staticmethod
    def list_recipes() -> ActionResult:
        """Lista todos los recipes disponibles."""
        try:
            recipes = []
            if os.path.exists(RECIPES_DIR):
                for filename in sorted(os.listdir(RECIPES_DIR)):
                    if filename.endswith('.json'):
                        recipe_path = os.path.join(RECIPES_DIR, filename)
                        try:
                            with open(recipe_path, 'r', encoding='utf-8') as f:
                                recipe = json.load(f)
                                recipes.append({
                                    "name": recipe.get("name", filename[:-5]),
                                    "description": recipe.get("description", ""),
                                    "filename": filename,
                                    "steps_count": len(recipe.get("steps", [])),
                                    "variables": list(recipe.get("variables", {}).keys()),
                                    "created_at": recipe.get("created_at", "")
                                })
                        except Exception:
                            recipes.append({
                                "name": filename[:-5],
                                "description": "Error al leer recipe",
                                "filename": filename,
                                "steps_count": 0,
                                "variables": [],
                                "created_at": ""
                            })
            
            return ActionResult(
                success=True,
                action="list_recipes",
                data={
                    "count": len(recipes),
                    "recipes": recipes
                }
            )
        except Exception as e:
            return ActionResult(success=False, action="list_recipes", error=str(e))
    
    @staticmethod
    def show_recipe(name: str) -> ActionResult:
        """Muestra el contenido de un recipe."""
        try:
            recipe_path = RecipeManager.get_recipe_path(name)
            
            # Intentar encontrar por nombre exacto o parcial
            if not os.path.exists(recipe_path):
                # Buscar coincidencia parcial
                for filename in os.listdir(RECIPES_DIR):
                    if filename.endswith('.json'):
                        if name.lower() in filename.lower():
                            recipe_path = os.path.join(RECIPES_DIR, filename)
                            break
            
            if not os.path.exists(recipe_path):
                return ActionResult(
                    success=False,
                    action="show_recipe",
                    error=f"Recipe no encontrado: {name}"
                )
            
            with open(recipe_path, 'r', encoding='utf-8') as f:
                recipe = json.load(f)
            
            return ActionResult(
                success=True,
                action="show_recipe",
                data=recipe
            )
        except Exception as e:
            return ActionResult(success=False, action="show_recipe", error=str(e))
    
    @staticmethod
    def delete_recipe(name: str) -> ActionResult:
        """Elimina un recipe."""
        try:
            recipe_path = RecipeManager.get_recipe_path(name)
            
            # Intentar encontrar por nombre exacto o parcial
            if not os.path.exists(recipe_path):
                for filename in os.listdir(RECIPES_DIR):
                    if filename.endswith('.json'):
                        if name.lower() in filename.lower():
                            recipe_path = os.path.join(RECIPES_DIR, filename)
                            break
            
            if not os.path.exists(recipe_path):
                return ActionResult(
                    success=False,
                    action="delete_recipe",
                    error=f"Recipe no encontrado: {name}"
                )
            
            os.remove(recipe_path)
            return ActionResult(
                success=True,
                action="delete_recipe",
                data={"deleted": name}
            )
        except Exception as e:
            return ActionResult(success=False, action="delete_recipe", error=str(e))
    
    @staticmethod
    def run_recipe(name: str, variable_values: Optional[Dict[str, str]] = None,
                   controller: Optional['BrowserController'] = None,
                   headless: bool = True, browser_type: str = "chromium") -> ActionResult:
        """Ejecuta un recipe."""
        try:
            # Cargar recipe
            show_result = RecipeManager.show_recipe(name)
            if not show_result.success:
                return show_result
            
            recipe = show_result.data
            steps = recipe.get("steps", [])
            variables = recipe.get("variables", {})
            
            # Mezclar variables con valores proporcionados
            exec_variables = variables.copy()
            if variable_values:
                exec_variables.update(variable_values)
            
            # Inicializar controlador si no se proporcionó
            own_controller = controller is None
            if own_controller:
                if not PLAYWRIGHT_AVAILABLE:
                    return ActionResult(
                        success=False,
                        action="run_recipe",
                        error="Playwright no está instalado. Ejecuta: pip install playwright && playwright install"
                    )
                controller = BrowserController(headless=headless, browser_type=browser_type)
                start_result = controller.start()
                if not start_result.success:
                    return start_result
            
            results = []
            final_result = None
            
            # Ejecutar cada paso
            for i, step in enumerate(steps):
                step_action = step.get("action")
                step_params = step.get("params", {})
                step_description = step.get("description", f"Paso {i+1}")
                
                # Reemplazar variables en parámetros
                processed_params = {}
                for key, value in step_params.items():
                    if isinstance(value, str):
                        # Reemplazar {{variable}} con su valor
                        for var_name, var_value in exec_variables.items():
                            value = value.replace(f"{{{{{var_name}}}}}", var_value)
                    processed_params[key] = value
                
                # Ejecutar acción
                result = controller.execute_action(step_action, processed_params)
                results.append({
                    "step": i + 1,
                    "description": step_description,
                    "action": step_action,
                    "result": result.to_dict()
                })
                
                final_result = result
                
                # Si un paso falla, detener ejecución
                if not result.success:
                    break
            
            # Cerrar controlador si lo creamos nosotros
            if own_controller:
                controller.stop()
            
            return ActionResult(
                success=final_result.success if final_result else True,
                action="run_recipe",
                data={
                    "recipe_name": recipe.get("name"),
                    "steps_executed": len(results),
                    "all_success": all(r["result"]["success"] for r in results),
                    "results": results,
                    "final_url": final_result.url if final_result else None,
                    "final_title": final_result.title if final_result else None
                }
            )
            
        except Exception as e:
            return ActionResult(success=False, action="run_recipe", error=str(e))


class BrowserController:
    """Controlador principal del navegador."""
    
    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    def start(self) -> ActionResult:
        """Inicia el navegador."""
        if not PLAYWRIGHT_AVAILABLE:
            return ActionResult(
                success=False,
                action="start",
                error="Playwright no está instalado. Ejecuta: pip install playwright && playwright install"
            )
        
        try:
            self.playwright = sync_playwright().start()
            
            if self.browser_type == "firefox":
                browser_class = self.playwright.firefox
            elif self.browser_type == "webkit":
                browser_class = self.playwright.webkit
            else:
                browser_class = self.playwright.chromium
            
            self.browser = browser_class.launch(headless=self.headless)
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self.page = self.context.new_page()
            
            return ActionResult(
                success=True,
                action="start",
                data={"browser": self.browser_type, "headless": self.headless}
            )
        except Exception as e:
            return ActionResult(success=False, action="start", error=str(e))
    
    def stop(self) -> ActionResult:
        """Cierra el navegador."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            return ActionResult(success=True, action="stop")
        except Exception as e:
            return ActionResult(success=False, action="stop", error=str(e))
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> ActionResult:
        """Ejecuta una acción con parámetros dinámicos."""
        action_map = {
            "navigate": lambda: self.navigate(params.get("url"), params.get("wait_until", "networkidle")),
            "click": lambda: self.click(params.get("selector"), params.get("timeout", 5000)),
            "fill": lambda: self.fill(params.get("selector"), params.get("text"), params.get("timeout", 5000)),
            "type": lambda: self.type_text(params.get("selector"), params.get("text"), 
                                           params.get("delay", 50), params.get("timeout", 5000)),
            "press_key": lambda: self.press_key(params.get("key")),
            "wait_for_selector": lambda: self.wait_for_selector(params.get("selector"), params.get("timeout", 5000)),
            "wait_for_load": lambda: self.wait_for_load(params.get("state", "networkidle")),
            "screenshot": lambda: self.screenshot(params.get("full_page", False), params.get("selector")),
            "get_text": lambda: self.get_text(params.get("selector")),
            "get_html": lambda: self.get_html(params.get("selector")),
            "evaluate": lambda: self.evaluate(params.get("script")),
            "scroll": lambda: self.scroll(params.get("direction", "down"), params.get("amount", 500)),
            "scroll_to_element": lambda: self.scroll_to_element(params.get("selector")),
            "select_option": lambda: self.select_option(params.get("selector"), params.get("value"), 
                                                          params.get("label"), params.get("index")),
            "get_attribute": lambda: self.get_attribute(params.get("selector"), params.get("attribute")),
            "get_elements": lambda: self.get_elements(params.get("selector")),
            "go_back": lambda: self.go_back(),
            "go_forward": lambda: self.go_forward(),
            "reload": lambda: self.reload(),
            "set_viewport": lambda: self.set_viewport(params.get("width", 1920), params.get("height", 1080)),
            "new_tab": lambda: self.new_tab(params.get("url")),
            "close_tab": lambda: self.close_tab(),
            "switch_tab": lambda: self.switch_tab(params.get("index", 0)),
            "list_tabs": lambda: self.list_tabs(),
            "handle_dialog": lambda: self.handle_dialog(params.get("accept", True), params.get("prompt_text")),
            "hover": lambda: self.hover(params.get("selector")),
            "focus": lambda: self.focus(params.get("selector")),
            "clear": lambda: self.clear(params.get("selector")),
            "check": lambda: self.check(params.get("selector"), params.get("checked", True)),
            "sleep": lambda: self.sleep(params.get("seconds", 1)),
        }
        
        if action in action_map:
            return action_map[action]()
        else:
            return ActionResult(success=False, action=action, error=f"Acción desconocida: {action}")
    
    def sleep(self, seconds: float) -> ActionResult:
        """Pausa la ejecución."""
        import time
        time.sleep(seconds)
        return ActionResult(success=True, action="sleep", data={"seconds": seconds})
    
    def navigate(self, url: str, wait_until: str = "networkidle") -> ActionResult:
        """Navega a una URL."""
        try:
            self.page.goto(url, wait_until=wait_until)
            return ActionResult(
                success=True,
                action="navigate",
                url=self.page.url,
                title=self.page.title()
            )
        except Exception as e:
            return ActionResult(success=False, action="navigate", error=str(e))
    
    def click(self, selector: str, timeout: int = 5000) -> ActionResult:
        """Hace clic en un elemento."""
        try:
            self.page.click(selector, timeout=timeout)
            return ActionResult(
                success=True,
                action="click",
                url=self.page.url,
                title=self.page.title()
            )
        except Exception as e:
            return ActionResult(success=False, action="click", error=str(e))
    
    def fill(self, selector: str, text: str, timeout: int = 5000) -> ActionResult:
        """Llena un campo de texto."""
        try:
            self.page.fill(selector, text, timeout=timeout)
            return ActionResult(
                success=True,
                action="fill",
                data={"selector": selector, "text": text}
            )
        except Exception as e:
            return ActionResult(success=False, action="fill", error=str(e))
    
    def type_text(self, selector: str, text: str, delay: int = 50, timeout: int = 5000) -> ActionResult:
        """Escribe texto carácter por carácter (simula tipeo humano)."""
        try:
            self.page.type(selector, text, delay=delay, timeout=timeout)
            return ActionResult(
                success=True,
                action="type",
                data={"selector": selector, "text": text}
            )
        except Exception as e:
            return ActionResult(success=False, action="type", error=str(e))
    
    def press_key(self, key: str) -> ActionResult:
        """Presiona una tecla especial (Enter, Escape, etc.)."""
        try:
            self.page.press("body", key)
            return ActionResult(
                success=True,
                action="press_key",
                data={"key": key}
            )
        except Exception as e:
            return ActionResult(success=False, action="press_key", error=str(e))
    
    def wait_for_selector(self, selector: str, timeout: int = 5000) -> ActionResult:
        """Espera a que un elemento aparezca."""
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            return ActionResult(
                success=True,
                action="wait_for_selector",
                data={"selector": selector, "found": element is not None}
            )
        except Exception as e:
            return ActionResult(success=False, action="wait_for_selector", error=str(e))
    
    def wait_for_load(self, state: str = "networkidle") -> ActionResult:
        """Espera a que la página cargue."""
        try:
            self.page.wait_for_load_state(state)
            return ActionResult(
                success=True,
                action="wait_for_load",
                data={"state": state}
            )
        except Exception as e:
            return ActionResult(success=False, action="wait_for_load", error=str(e))
    
    def screenshot(self, full_page: bool = False, selector: Optional[str] = None) -> ActionResult:
        """Toma una captura de pantalla."""
        try:
            if selector:
                element = self.page.query_selector(selector)
                if not element:
                    return ActionResult(
                        success=False,
                        action="screenshot",
                        error=f"Elemento no encontrado: {selector}"
                    )
                screenshot_bytes = element.screenshot()
            else:
                screenshot_bytes = self.page.screenshot(full_page=full_page)
            
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return ActionResult(
                success=True,
                action="screenshot",
                screenshot=screenshot_b64,
                url=self.page.url,
                title=self.page.title()
            )
        except Exception as e:
            return ActionResult(success=False, action="screenshot", error=str(e))
    
    def get_text(self, selector: Optional[str] = None) -> ActionResult:
        """Extrae texto de la página o de un elemento específico."""
        try:
            if selector:
                element = self.page.query_selector(selector)
                if not element:
                    return ActionResult(
                        success=False,
                        action="get_text",
                        error=f"Elemento no encontrado: {selector}"
                    )
                text = element.inner_text()
            else:
                text = self.page.inner_text("body")
            
            return ActionResult(
                success=True,
                action="get_text",
                data={"text": text}
            )
        except Exception as e:
            return ActionResult(success=False, action="get_text", error=str(e))
    
    def get_html(self, selector: Optional[str] = None) -> ActionResult:
        """Obtiene el HTML de la página o de un elemento."""
        try:
            if selector:
                element = self.page.query_selector(selector)
                if not element:
                    return ActionResult(
                        success=False,
                        action="get_html",
                        error=f"Elemento no encontrado: {selector}"
                    )
                html = element.inner_html()
            else:
                html = self.page.content()
            
            return ActionResult(
                success=True,
                action="get_html",
                data={"html": html}
            )
        except Exception as e:
            return ActionResult(success=False, action="get_html", error=str(e))
    
    def evaluate(self, script: str) -> ActionResult:
        """Ejecuta JavaScript en la página."""
        try:
            result = self.page.evaluate(script)
            return ActionResult(
                success=True,
                action="evaluate",
                data={"result": result}
            )
        except Exception as e:
            return ActionResult(success=False, action="evaluate", error=str(e))
    
    def scroll(self, direction: str = "down", amount: int = 500) -> ActionResult:
        """Hace scroll en la página."""
        try:
            if direction == "down":
                self.page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                self.page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction == "bottom":
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif direction == "top":
                self.page.evaluate("window.scrollTo(0, 0)")
            elif direction == "to":
                self.page.evaluate(f"window.scrollTo(0, {amount})")
            
            return ActionResult(
                success=True,
                action="scroll",
                data={"direction": direction, "amount": amount}
            )
        except Exception as e:
            return ActionResult(success=False, action="scroll", error=str(e))
    
    def scroll_to_element(self, selector: str) -> ActionResult:
        """Hace scroll hasta un elemento."""
        try:
            element = self.page.query_selector(selector)
            if element:
                element.scroll_into_view_if_needed()
                return ActionResult(success=True, action="scroll_to_element")
            else:
                return ActionResult(
                    success=False,
                    action="scroll_to_element",
                    error=f"Elemento no encontrado: {selector}"
                )
        except Exception as e:
            return ActionResult(success=False, action="scroll_to_element", error=str(e))
    
    def select_option(self, selector: str, value: Optional[str] = None, 
                      label: Optional[str] = None, index: Optional[int] = None) -> ActionResult:
        """Selecciona una opción de un dropdown."""
        try:
            if value:
                self.page.select_option(selector, value=value)
            elif label:
                self.page.select_option(selector, label=label)
            elif index is not None:
                self.page.select_option(selector, index=index)
            else:
                return ActionResult(
                    success=False,
                    action="select_option",
                    error="Debe especificar value, label o index"
                )
            
            return ActionResult(success=True, action="select_option")
        except Exception as e:
            return ActionResult(success=False, action="select_option", error=str(e))
    
    def get_attribute(self, selector: str, attribute: str) -> ActionResult:
        """Obtiene el valor de un atributo de un elemento."""
        try:
            value = self.page.get_attribute(selector, attribute)
            return ActionResult(
                success=True,
                action="get_attribute",
                data={"value": value}
            )
        except Exception as e:
            return ActionResult(success=False, action="get_attribute", error=str(e))
    
    def get_elements(self, selector: str) -> ActionResult:
        """Obtiene información de todos los elementos que coinciden con el selector."""
        try:
            elements = self.page.query_selector_all(selector)
            results = []
            for i, element in enumerate(elements):
                try:
                    results.append({
                        "index": i,
                        "text": element.inner_text()[:100] if element.inner_text() else "",
                        "tag": element.evaluate("el => el.tagName.toLowerCase()")
                    })
                except:
                    results.append({"index": i, "error": "No se pudo extraer info"})
            
            return ActionResult(
                success=True,
                action="get_elements",
                data={"count": len(elements), "elements": results}
            )
        except Exception as e:
            return ActionResult(success=False, action="get_elements", error=str(e))
    
    def go_back(self) -> ActionResult:
        """Navega hacia atrás."""
        try:
            self.page.go_back()
            return ActionResult(
                success=True,
                action="go_back",
                url=self.page.url,
                title=self.page.title()
            )
        except Exception as e:
            return ActionResult(success=False, action="go_back", error=str(e))
    
    def go_forward(self) -> ActionResult:
        """Navega hacia adelante."""
        try:
            self.page.go_forward()
            return ActionResult(
                success=True,
                action="go_forward",
                url=self.page.url,
                title=self.page.title()
            )
        except Exception as e:
            return ActionResult(success=False, action="go_forward", error=str(e))
    
    def reload(self) -> ActionResult:
        """Recarga la página."""
        try:
            self.page.reload()
            return ActionResult(
                success=True,
                action="reload",
                url=self.page.url,
                title=self.page.title()
            )
        except Exception as e:
            return ActionResult(success=False, action="reload", error=str(e))
    
    def set_viewport(self, width: int, height: int) -> ActionResult:
        """Cambia el tamaño de la ventana."""
        try:
            self.page.set_viewport_size({"width": width, "height": height})
            return ActionResult(
                success=True,
                action="set_viewport",
                data={"width": width, "height": height}
            )
        except Exception as e:
            return ActionResult(success=False, action="set_viewport", error=str(e))
    
    def new_tab(self, url: Optional[str] = None) -> ActionResult:
        """Abre una nueva pestaña."""
        try:
            new_page = self.context.new_page()
            if url:
                new_page.goto(url)
            # Cambiar a la nueva página
            self.page = new_page
            return ActionResult(
                success=True,
                action="new_tab",
                url=self.page.url,
                title=self.page.title()
            )
        except Exception as e:
            return ActionResult(success=False, action="new_tab", error=str(e))
    
    def close_tab(self) -> ActionResult:
        """Cierra la pestaña actual."""
        try:
            self.page.close()
            # Volver a la primera página disponible
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            return ActionResult(
                success=True,
                action="close_tab",
                url=self.page.url if self.page else None
            )
        except Exception as e:
            return ActionResult(success=False, action="close_tab", error=str(e))
    
    def switch_tab(self, index: int = 0) -> ActionResult:
        """Cambia a otra pestaña por índice."""
        try:
            pages = self.context.pages
            if 0 <= index < len(pages):
                self.page = pages[index]
                return ActionResult(
                    success=True,
                    action="switch_tab",
                    url=self.page.url,
                    title=self.page.title()
                )
            else:
                return ActionResult(
                    success=False,
                    action="switch_tab",
                    error=f"Índice inválido. Hay {len(pages)} pestañas."
                )
        except Exception as e:
            return ActionResult(success=False, action="switch_tab", error=str(e))
    
    def list_tabs(self) -> ActionResult:
        """Lista todas las pestañas abiertas."""
        try:
            pages = self.context.pages
            tabs = []
            for i, page in enumerate(pages):
                tabs.append({
                    "index": i,
                    "url": page.url,
                    "title": page.title()
                })
            return ActionResult(
                success=True,
                action="list_tabs",
                data={"tabs": tabs, "count": len(tabs)}
            )
        except Exception as e:
            return ActionResult(success=False, action="list_tabs", error=str(e))
    
    def handle_dialog(self, accept: bool = True, prompt_text: Optional[str] = None) -> ActionResult:
        """Configura el manejo de diálogos (alert, confirm, prompt)."""
        try:
            def dialog_handler(dialog):
                if accept:
                    if prompt_text and dialog.type == "prompt":
                        dialog.accept(prompt_text)
                    else:
                        dialog.accept()
                else:
                    dialog.dismiss()
            
            self.page.on("dialog", dialog_handler)
            return ActionResult(
                success=True,
                action="handle_dialog",
                data={"accept": accept}
            )
        except Exception as e:
            return ActionResult(success=False, action="handle_dialog", error=str(e))
    
    def hover(self, selector: str) -> ActionResult:
        """Hace hover sobre un elemento."""
        try:
            self.page.hover(selector)
            return ActionResult(success=True, action="hover")
        except Exception as e:
            return ActionResult(success=False, action="hover", error=str(e))
    
    def focus(self, selector: str) -> ActionResult:
        """Enfoca un elemento."""
        try:
            self.page.focus(selector)
            return ActionResult(success=True, action="focus")
        except Exception as e:
            return ActionResult(success=False, action="focus", error=str(e))
    
    def clear(self, selector: str) -> ActionResult:
        """Limpia un campo de texto."""
        try:
            self.page.fill(selector, "")
            return ActionResult(success=True, action="clear")
        except Exception as e:
            return ActionResult(success=False, action="clear", error=str(e))
    
    def check(self, selector: str, checked: bool = True) -> ActionResult:
        """Marca o desmarca un checkbox."""
        try:
            if checked:
                self.page.check(selector)
            else:
                self.page.uncheck(selector)
            return ActionResult(success=True, action="check", data={"checked": checked})
        except Exception as e:
            return ActionResult(success=False, action="check", error=str(e))


def main():
    parser = argparse.ArgumentParser(description="Browser Controller")
    
    # Acciones básicas
    parser.add_argument("--action", "-a", help="Acción a ejecutar")
    parser.add_argument("--url", help="URL para navegar")
    parser.add_argument("--selector", "-s", help="Selector CSS del elemento")
    parser.add_argument("--text", "-t", help="Texto para escribir")
    parser.add_argument("--key", help="Tecla a presionar")
    parser.add_argument("--attribute", help="Atributo a obtener")
    parser.add_argument("--value", help="Valor para select/checkbox")
    parser.add_argument("--label", help="Label para select")
    parser.add_argument("--index", type=int, help="Índice numérico")
    parser.add_argument("--direction", default="down", help="Dirección del scroll")
    parser.add_argument("--amount", type=int, default=500, help="Cantidad de scroll")
    parser.add_argument("--width", type=int, help="Ancho de viewport")
    parser.add_argument("--height", type=int, help="Alto de viewport")
    parser.add_argument("--timeout", type=int, default=5000, help="Timeout en ms")
    parser.add_argument("--delay", type=int, default=50, help="Delay entre teclas")
    parser.add_argument("--full-page", action="store_true", help="Screenshot de página completa")
    parser.add_argument("--headless", action="store_true", default=True, help="Modo headless")
    parser.add_argument("--browser", default="chromium", choices=["chromium", "firefox", "webkit"])
    parser.add_argument("--download-path", help="Ruta para descargar archivos")
    parser.add_argument("--prompt-text", help="Texto para prompt dialogs")
    parser.add_argument("--accept", type=lambda x: x.lower() == 'true', default=True, help="Aceptar/dismiss dialog")
    parser.add_argument("--script", help="JavaScript a ejecutar")
    parser.add_argument("--seconds", type=float, default=1, help="Segundos para sleep")
    
    # Acciones de recipes
    parser.add_argument("--create-recipe", help="Nombre del nuevo recipe a crear")
    parser.add_argument("--description", "-d", help="Descripción del recipe")
    parser.add_argument("--steps", help="Pasos del recipe en formato JSON string")
    parser.add_argument("--steps-file", help="Archivo JSON con los pasos del recipe")
    parser.add_argument("--variables", help="Variables del recipe en formato JSON")
    parser.add_argument("--run-recipe", help="Nombre del recipe a ejecutar")
    parser.add_argument("--show-recipe", help="Mostrar contenido de un recipe")
    parser.add_argument("--delete-recipe", help="Eliminar un recipe")
    parser.add_argument("--list-recipes", action="store_true", help="Listar todos los recipes")
    parser.add_argument("--var", action="append", help="Valores de variables (formato: nombre=valor)", default=[])
    
    args = parser.parse_args()
    
    # ===== GESTIÓN DE RECIPES =====
    
    # Listar recipes
    if args.list_recipes:
        result = RecipeManager.list_recipes()
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(0 if result.success else 1)
    
    # Mostrar recipe
    if args.show_recipe:
        result = RecipeManager.show_recipe(args.show_recipe)
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(0 if result.success else 1)
    
    # Eliminar recipe
    if args.delete_recipe:
        result = RecipeManager.delete_recipe(args.delete_recipe)
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(0 if result.success else 1)
    
    # Crear recipe
    if args.create_recipe:
        # Cargar pasos desde archivo o argumento
        if args.steps_file:
            with open(args.steps_file, 'r', encoding='utf-8-sig') as f:
                steps = json.load(f)
        elif args.steps:
            steps = json.loads(args.steps)
        else:
            # Crear un recipe básico de ejemplo si no se proporcionan pasos
            steps = [
                {"action": "navigate", "params": {"url": "https://example.com"}, "description": "Navegar al sitio"},
                {"action": "screenshot", "params": {"full_page": True}, "description": "Capturar pantalla"}
            ]
        
        # Parsear variables
        variables = {}
        if args.variables:
            variables = json.loads(args.variables)
        
        result = RecipeManager.create_recipe(
            name=args.create_recipe,
            description=args.description or f"Recipe: {args.create_recipe}",
            steps=steps,
            variables=variables
        )
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(0 if result.success else 1)
    
    # Ejecutar recipe
    if args.run_recipe:
        # Parsear variables de línea de comandos
        variable_values = {}
        for var in args.var:
            if '=' in var:
                name, value = var.split('=', 1)
                variable_values[name] = value
        
        result = RecipeManager.run_recipe(
            name=args.run_recipe,
            variable_values=variable_values,
            headless=args.headless,
            browser_type=args.browser
        )
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(0 if result.success else 1)
    
    # ===== ACCIONES BÁSICAS =====
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    # Inicializar controlador
    controller = BrowserController(headless=args.headless, browser_type=args.browser)
    
    # Acciones que requieren navegador iniciado
    actions_requiring_browser = [
        "navigate", "click", "fill", "type", "press_key", "wait_for_selector",
        "wait_for_load", "screenshot", "get_text", "get_html", "evaluate",
        "scroll", "scroll_to_element", "select_option", "get_attribute",
        "get_elements", "go_back", "go_forward", "reload", "set_viewport",
        "new_tab", "close_tab", "switch_tab", "list_tabs", "handle_dialog",
        "hover", "focus", "clear", "check", "sleep"
    ]
    
    # Iniciar navegador si es necesario
    if args.action in ["start"] + actions_requiring_browser:
        result = controller.start()
        if not result.success:
            print(json.dumps(result.to_dict(), indent=2))
            sys.exit(1)
    
    # Ejecutar acción
    params = {
        "url": args.url,
        "selector": args.selector,
        "text": args.text,
        "key": args.key,
        "attribute": args.attribute,
        "value": args.value,
        "label": args.label,
        "index": args.index,
        "direction": args.direction,
        "amount": args.amount,
        "width": args.width,
        "height": args.height,
        "timeout": args.timeout,
        "delay": args.delay,
        "full_page": args.full_page,
        "script": args.script,
        "state": args.value,
        "seconds": args.seconds,
        "checked": args.accept
    }
    # Eliminar parámetros None
    params = {k: v for k, v in params.items() if v is not None}
    
    result = controller.execute_action(args.action, params)
    
    # Imprimir resultado como JSON
    print(json.dumps(result.to_dict(), indent=2))
    
    # Cerrar navegador
    if args.action != "stop":
        controller.stop()
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
