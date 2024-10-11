import bpy
import json
import os

def export_compositor_node_data(output_file):
    # Ensure compositing nodes are enabled
    scene = bpy.context.scene
    if not scene.use_nodes:
        print("Compositing nodes are not enabled in the current scene.")
        return

    # Get the compositor node tree
    nodes = scene.node_tree.nodes
    links = scene.node_tree.links

    # Get Blender version
    blender_version = bpy.app.version_string

    # Prepare the data structure
    node_data = {
        "blender_version": blender_version,
        "nodes": [],
        "links": []
    }

    # Helper function to convert properties to a JSON-friendly format
    def convert_property(value):
        try:
            # Handle common iterable types
            if isinstance(value, (list, tuple)):
                return [convert_property(v) for v in value]
            # Convert vector-like properties to list
            elif hasattr(value, "to_list"):
                return list(value)
            # Handle scalar values (float, int, str)
            elif isinstance(value, (float, int, str)):
                return value
            # Convert other types to string for logging purposes
            return str(value)
        except Exception as e:
            return str(value)  # Fallback conversion to avoid errors

    # Export each node's data
    for node in nodes:
        node_info = {
            "name": node.name,
            "type": node.bl_idname,
            "location": [node.location.x, node.location.y],
            "inputs": [],
            "outputs": [],
            "settings": {}
        }

        # Capture inputs with their default values if applicable
        for input_socket in node.inputs:
            input_info = {
                "name": input_socket.name,
                "type": input_socket.type,
                "default_value": convert_property(getattr(input_socket, 'default_value', None))
            }
            node_info["inputs"].append(input_info)

        # Capture outputs
        for output_socket in node.outputs:
            output_info = {
                "name": output_socket.name,
                "type": output_socket.type
            }
            node_info["outputs"].append(output_info)

        # Capture additional node-specific settings (e.g., dropdowns, properties)
        for prop_name in node.bl_rna.properties.keys():
            if prop_name not in {"inputs", "outputs", "bl_idname", "location", "name"}:
                try:
                    value = getattr(node, prop_name)
                    node_info["settings"][prop_name] = convert_property(value)
                except AttributeError:
                    pass  # Ignore properties that can't be accessed directly

        # Special handling for CompositorNodeValue to ensure the default value is captured
        if node.bl_idname == "CompositorNodeValue":
            node_info["value"] = convert_property(node.outputs[0].default_value or node.value)


        node_data["nodes"].append(node_info)

    # Export each link's data
    for link in links:
        link_info = {
            "from_node": link.from_node.name,
            "from_socket": link.from_socket.name,
            "to_node": link.to_node.name,
            "to_socket": link.to_socket.name
        }
        node_data["links"].append(link_info)

    # Write the data to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(node_data, json_file, indent=4)

    print(f"Compositor node data exported to {output_file}")

# Example usage:
output_file = os.path.join(bpy.path.abspath("//"), "compositor_shader.json")
export_compositor_node_data(output_file)
