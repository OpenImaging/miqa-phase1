---

# Edit the frontmatter for all the homepage sections. To make edits to the about content, scroll down past the frontmatter and edit the markdown.

permalink: /
layout: homepage

# Hero
hero_image: 'img/fluids_blend.png'
hero_attribution: '<strong>Image Credit:</strong> Matthew Larsen, LLNL. This image is of an idealized Inertial Confinement Fusion (ICF) simulation of a Rayleigh-Taylor instability with two fluids mixing in a spherical geometry.'

# Download CTA
download_title: Getting started
download_message: >-
  <p>Download the latest release and then follow the instructions. If you're not already a VTK user and want to learn more about the original toolkit, <a href="http://vtk.org" target="_blank">check it out</a>.</p>
download_link: 'https://gitlab.kitware.com/vtk/vtk-m/-/releases'

# Resources
resources_title: VTK-m Resources
resources_blurb: >-
  <p class="text-xs">Are you funded by the ECP/VTK-m project? See <a href="https://m.vtk.org/index.php/ECP/VTK-m_project_management" target="_blank">ECP/VTK-m project management</a>.</p>

resources:
  - name: Building VTK-m
    icon: ri-stack-fill
    link: 'https://gitlab.kitware.com/vtk/vtk-m/blob/master/README.md#building'
  - name: Software Dependencies
    icon: ri-terminal-box-fill
    link: 'https://gitlab.kitware.com/vtk/vtk-m/blob/master/README.md#dependencies'
  - name: Contributing
    icon: ri-chat-check-fill
    link: 'https://gitlab.kitware.com/vtk/vtk-m/blob/master/CONTRIBUTING.md'
  - name: Mailing List
    icon: ri-send-plane-fill
    link: 'http://vtk.org/mailman/listinfo/vtkm'
  - name: User Guide
    icon: ri-book-2-fill
    link: 'https://gitlab.kitware.com/vtk/vtk-m-user-guide/-/wikis/home'
  - name: Doxygen Documentation
    icon: ri-booklet-fill
    link: 'http://m.vtk.org/documentation/'
  - name: Tutorial
    icon: ri-lightbulb-flash-fill
    link: '/tutorial'
  - name: VTK-m Assets
    icon: ri-database-line
    link: '/assets'

# Publications
publications: true
pubs_title: VTK-m Publications
pubs_blurb: >-
  <p>Please use the first paper when referencing VTK-m in scientific publications.</p>

---

# What is VTK-m?

One of the biggest recent changes in high-performance computing is the increasing use of accelerators. Accelerators contain processing cores that independently are inferior to a core in a typical CPU, but these cores are replicated and grouped such that their aggregate execution provides a very high computation rate at a much lower power. Current and future CPU processors also require much more explicit parallelism. Each successive version of the hardware packs more cores into each processor, and technologies like hyperthreading and vector operations require even more parallel processing to leverage each core’s full potential.

**VTK-m is a toolkit of scientific visualization algorithms for emerging processor architectures.** VTK-m supports the fine-grained concurrency for data analysis and visualization algorithms required to drive extreme scale computing by providing abstract models for data and execution that can be applied to a variety of algorithms across many different processor architectures.
