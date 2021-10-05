<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/wine-uoc/lora_simulator/tree/aaron">
    <img src="images/WiNe_logo.png" alt="Logo" width="200" height="80">
  </a>

  <h3 align="center">Simulator for LoRa/LoRa-E networks.</h3>

  <p align="center">
    Simulator for 
    <br />
    <a href="https://github.com/wine-uoc/lora_simulator/tree/aaron"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/wine-uoc/lora_simulator/tree/aaron">View Demo</a>
    ·
    <a href="https://github.com/wine-uoc/lora_simulator/tree/aaron/issues">Report Bug</a>
    ·
    <a href="https://github.com/wine-uoc/lora_simulator/tree/aaron/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
# About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Explain: 

* What this project is intended for.
* 

# Built With


* [Python 3.7.9](https://www.python.org/)

<!-- GETTING STARTED -->
# Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

1. Clone the repo
   ```sh
   $> git clone https://github.com/wine-uoc/lora_simulator.git -b aaron
   ```
2. Install required third-party libraries for Python
    ```sh
    $> pip3 install -r requirements.txt
    ```

<!-- USAGE EXAMPLES -->
# Usage

* In ``Simulator.yaml`` file, set the [parameters values](#parameters-description) for the simulation. 

* Run ``run_pool.py`` script to start simulations:
    ```sh
    $> python3 run_pool.py
    ```

* Results of simulations will be saved in the directory specified in ``root_dir_name`` field from ``Simulator.yaml`` file.


_For more examples, please refer to the [Documentation](https://example.com)_

# Parameters description

A file named ``Simulator.yaml`` holds the parameters related to simulations. Their values can be modified to simulate the desired scenario. A description for these parameters is provided in this section to better understand the purpose of each one of them.

*  ``root_dir_name``: Root directory where simulation results will be saved
*  ``area_side_size``: Size of the simulation area side in meters (assuming squared map)
*  ``time``: Duration of the simulation in milliseconds.
*  ``step``: Time step of the simulation in milliseconds.
*  ``interval``: Transmit interval for each device in milliseconds.
*  ``position_mode``: Set devices position mode. Valid values:
   *  _normal_: devices are placed following a normal distribution.
   *  _uniform_: devices are placed following an uniform distribution.
   *  _circle_: devices are placed in a circle around the gateway.
   *  _annulus_: devices are placed in an annulus around the gateway.
*  ``position_mode_values``: 
   *  _$r$ $R$_ if ``position_mode``=_annulus_. (inner radius and outer radius)
   *   _$\sigma$_ if ``position_mode``=_normal_. (std. deviation)
*  ``time_mode``: Time error mode for transmitting devices. Valid values: 
   *  _deterministic_: devices transmit after a fixed amount of time (off_period).  
   *  _normal_: devices transmit following a normal distribution pattern. 
   *  _uniform_: devices transmit following a uniform distribution pattern. 
   *  _expo_: devices transmit following an exponential distribution pattern. 
   *  _naive_: the first transmission of each device is random. The next transmissions are deterministic.
*  ``payload_size``: Payload size in bytes.
*  ``random``: Determine if simulation is random or not. Valid values:
   *  _0_: Deterministic
   *  _1_: Random
*  ``devices_tx_power``: Transmission power of devices in dBm.
*  ``num_runs``: Number of repetitions of the experiment
*  ``LoRa_auto_DR_selection``: Determines if LoRa data rate selection is automatic depending on the distance node-GW or not. Valid values:
   *  _0_: DR selection is not automatic.
   *  _1_: DR selection is automatic.
*  ``n_LoRa_devices``: Set of numbers of LoRa devices to simulate.
*  ``LoRa_data_rates``: Set of LoRa data rates to simulate. Valid values: _0_-_5_.
*  ``n_LoRa_E_devices``: Set of numbers of LoRa-E devices to simulate.
*  ``LoRa_E_data_rates``: Set of LoRa-E data rates to simulate. Valid values: _8_, _9_

# Architecture

## Class diagram

Classes relationships in the simulator are provided to get an overview of the system.

![image](https://github.com/wine-uoc/lora_simulator/blob/aaron/images/ClassDiagram.png)


## Performance

*  Execution of run_pool.py
    * 

<!-- ROADMAP -->
# Roadmap

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a list of proposed features (and known issues).


<!-- CONTRIBUTING -->
# Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


# Authors

* **Andrés Villanueva** - *Trabajo Inicial* - [villanuevand](https://github.com/villanuevand)
* **Fulanito Detal** - *Documentación* - [fulanitodetal](#fulanito-de-tal)

<!-- LICENSE -->
# License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
# Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)


<!-- ACKNOWLEDGEMENTS -->
# Acknowledgements
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Img Shields](https://shields.io)
* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Pages](https://pages.github.com)
* [Animate.css](https://daneden.github.io/animate.css)
* [Loaders.css](https://connoratherton.com/loaders)
* [Slick Carousel](https://kenwheeler.github.io/slick)
* [Smooth Scroll](https://github.com/cferdinandi/smooth-scroll)
* [Sticky Kit](http://leafo.net/sticky-kit)
* [JVectorMap](http://jvectormap.com)
* [Font Awesome](https://fontawesome.com)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/wine-uoc/lora_simulator?style=for-the-badge
[contributors-url]: https://github.com/wine-uoc/lora_simulator/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/wine-uoc/lora_simulator?style=for-the-badge
[forks-url]: https://github.com/wine-uoc/lora_simulator/network/members
[stars-shield]: https://img.shields.io/github/stars/wine-uoc/lora_simulator?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/wine-uoc/lora_simulator?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/wine-uoc/lora_simulator?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png

[![GitHub issues](https://img.shields.io/github/issues/wine-uoc/lora_simulator)](https://github.com/wine-uoc/lora_simulator/issues)
