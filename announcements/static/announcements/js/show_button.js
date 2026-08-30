export function initShowButtons(root = document) {
  const buttons = root.querySelectorAll(".show-button");

  buttons.forEach(button => {
    button.addEventListener("click", function () {
      const replaceContent = this.getAttribute("data-replace");
      this.innerHTML = replaceContent;
      this.disabled = true;
    });
  });
}