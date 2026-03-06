# Label Visualization Tool for X-AIGD Dataset

## X-AIGD Dataset

- X-AIGD contains human annotations of artifacts in generated images, which are categorized and localized.
- Important data fields:
    - `image`: The AI-generated image (loaded as a PIL Image object).
    - `generator`: Name of the text-to-image generator.
    - `uid`: Unique identifier for the image. Fake images across different generators can share the same UID.
    - `labels`: List of human-annotated artifacts, each containing:
        - `label`: Category of the artifact (7 possible values: low-level-edge_shape, low-level-texture, low-level-color, low-level-symbol, high-level-semantics, cognitive-level-commonsense, cognitive-level-physics).
        - `points`: Polygon coordinates `[[x1, y1], [x2, y2], ...]` localizing the artifact.
    - `width`, `height`: Image resolution.


## Visualization Tool

- The tool will visualize the annotated artifacts on the images, allowing users to see the categories and locations of the artifacts.
- Features:
    - Display the image with overlaid polygons for each artifact.
    - Color-code the polygons based on their categories.
    - Select a category to filter and display only the relevant artifacts.
        - When a category is selected, only show the images that contain artifacts of that category.
        - When no category is selected, show all images with their respective artifacts.
        - Changing the category selection should not update the image currently being viewed, even if the current image does not contain artifacts of the newly selected category. The user can manually navigate to other images to see the effects of the category selection.
    - Show the generator name and UID for reference.
    - Buttons and keyboard shortcuts for navigation and category selection.

