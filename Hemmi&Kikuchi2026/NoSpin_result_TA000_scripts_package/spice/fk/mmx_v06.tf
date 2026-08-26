KPL/FK

MMX Frames Definition Kernel
==============================================================================

   This frame kernel contains a set of frame definitions for the Martian
   Moons Exploration (MMX) mission. It also contains NAIF name-ID mappings
   for MMX instruments.


Version and Date
------------------------------------------------------------------------------

   Version 0.6 -- October 29, 2025 -- Shin-ya Murakami, ISAS/JAXA

      - Changed frame's center to be -239 for most of the frames definitions.
      - Fixed the MMX_MIRS_SCAN_MEAS frame definition.


   Version 0.5 -- May 9, 2024 -- Shin-ya Murakami, ISAS/JAXA

      - Removed unnecessary extra definition of the MMX_MIRS_SCAN frame.


   Version 0.4 -- March 7, 2024 -- Shin-ya Murakami, ISAS/JAXA

      - Introduced Switch frames; the MMX_SPACECRAFT, MMX_SAP1, MMX_SAP2,
        MMX_XMGA, MMX_MIRS_SCAN frames are replaced with Switch frames,
        updated the MMX Frames Summary, the Reference Frame tree, and
        descriptions for each frames.

   Version 0.3 -- August 9, 2023 -- Shin-ya Murakami, ISAS/JAXA

      - Removed MMX_XMGA-MX and MMX_XMGA-PX frames and added MMX_XMGA_BASE
        and MMX_XMGA frames.
      - Updated descriptions on antenna frames.
      - Updated the Reference Frame tree.

   Version 0.2 -- August 3, 2023 -- Shin-ya Murakami, ISAS/JAXA

      - Renamed MMX_CAM-W-A and MMX_CAM-W-B to MMX_CAM-W1 and MMX_CAM-W2.
      - Renamed MMX_ALT-A and MMX_ALT-B to MMX_ALT1 and MMX_ALT2.
      - Fixed an ASCII diagram in the Navigation Camera Frames definition
        section.
      - Fixed the MMX_SHV_MSC and MMX_SHV_SSC frame definitions.
      - Updated the definition of MMX_SPACECRAFT.
      - Added Solar Array Paddle Frames definition.
      - Changed origins of most of frames using an instrument position SPK.
      - Updated rotation angles for MMX_MSA_MG-S1 and MMX_MSA_MG-S2.

   Version 0.1 -- July 11, 2023 -- Shin-ya Murakami, ISAS/JAXA

      - Updated description of the MEGANE frames based on [11].
      - Updated TENGOO frame based on [12].
      - Added CAM-T frame based on [13].

   Version 0.0 -- February 7, 2023 -- Shin-ya Murakami, ISAS/JAXA

      - Created draft version.


References
------------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``C-Kernel Required Reading''

   4. Martian Moons Exploration (MMX) Spacecraft Attitude Baseline,
      1st Edition, JAXA, November 16, 2021, JX-ESPC-102129-NC.

   5. MXS-E-22-016_mission_instrument_layout_20220425.pdf

   6. MMX SHV SOOH part 1 NC draft, September 12, 2022.

   7. MMX CMDM SOOH part 1 draft, July 1, 2022.

   8. MMX LIDAR SOOH part 1 draft, August 1, 2022.

   9. MIRS Interface Control Document (ICD), JAXA, December 5, 2022,
      JX-ESPC-101977-B.

   10. MMX MSA SOOH part 1, July 23, 2022.

   11. MMX IREM SOOH part 1 draft, August 30, 2022.

   12. MMX TENGOO SOOH part 1 draft, July 29, 2022.

   13. MMX OROCHI SOOH part 1 draft, July 31, 2022.

   14. Email communication from Hiroki Kusano at February 27, 2023.

   15. Email communication from Naoya Sakatani at March 1, 2023.

   16. Email communication from Hiroshi Kikuchi at July 5, 2023.

   17. MMX SOOH part 1: Spacecraft System Explanation, Draft 2, May 30, 2023.


Contact Information
------------------------------------------------------------------------------

   Shin-ya Murakami, ISAS/JAXA, murakami.shinya@jaxa.jp


MMX Frames Summary
------------------------------------------------------------------------------

   The following MMX frames are defined in this kernel file:

   Landing sites:
   --------------
      Name                   Relative to            Type        Frame ID
      ====================   ====================   =========   ========
      MMX_LANDING_SITE_1     IAU_PHOBOS             FIXED       -239900
      MMX_LANDING_SITE_2     IAU_PHOBOS             FIXED       -239901
      MMX_SITE_1             IAU_PHOBOS             FIXED       -239700
               ...
      MMX_SITE_200           IAU_PHOBOS             FIXED       -239899


   Dynamic Frames:
   ---------------
      Name                   Relative to            Type        Frame ID
      ====================   ====================   =========   ========
      PHOBOS_MARS_P          J2000                  DYNAMIC     -239910
      DEIMOS_MARS_P          J2000                  DYNAMIC     -239911
      MMX_MARS_P             J2000                  DYNAMIC     -239912
      MMX_PHOBOS_P           J2000                  DYNAMIC     -239913
      MMX_DEIMOS_P           J2000                  DYNAMIC     -239914


   Spacecraft and the rover frames:
   --------------------------------
      Name                   Relative to            Type        Frame ID
      ====================   ====================   =========   ========
      MMX_SPACECRAFT                                SWITCH      -239000
      MMX_SPACECRAFT_PLAN    J2000                  CK          -239001
      MMX_SPACECRAFT_MEAS    J2000                  CK          -239002
      MMX_ROVER              IAU_PHOBOS             CK          -239600


   Bus frames (solar arrays, antennas, etc.):
   ------------------------------------------
      Name                   Relative to            Type        Frame ID
      ====================   ====================   =========   ========
      MMX_SAP1_BASE          MMX_SPACECRAFT         FIXED       -239010
      MMX_SAP1                                      SWITCH      -239011
      MMX_SAP1_PLAN          MMX_SAP1_BASE          CK          -239012
      MMX_SAP1_MEAS          MMX_SAP1_BASE          CK          -239013
      MMX_SAP2_BASE          MMX_SPACECRAFT         FIXED       -239014
      MMX_SAP2                                      SWITCH      -239015
      MMX_SAP2_PLAN          MMX_SAP2_BASE          CK          -239016
      MMX_SAP2_MEAS          MMX_SAP2_BASE          CK          -239017
      MMX_SAP_NOMINAL        MMX_SPACECRAFT         DYNAMIC     -239018

      MMX_KAXHGA             MMX_SPACECRAFT         FIXED       -239020
      MMX_XLGA-PX            MMX_SPACECRAFT         FIXED       -239021
      MMX_XLGA-PZ            MMX_SPACECRAFT         FIXED       -239022
      MMX_XLGA-MX            MMX_SPACECRAFT         FIXED       -239023
      MMX_XMGA_BASE          MMX_SPACECRAFT         FIXED       -239024
      MMX_XMGA                                      SWITCH      -239025
      MMX_XMGA_PLAN          MMX_XMGA_BASE          CK          -239026
      MMX_XMGA_MEAS          MMX_XMGA_BASE          CK          -239027

      MMX_ALT1               MMX_SPACECRAFT         FIXED       -239030
      MMX_ALT2               MMX_SPACECRAFT         FIXED       -239031

      MMX_CAM-T              MMX_SPACECRAFT         FIXED       -239040
      MMX_CAM-W1             MMX_SPACECRAFT         FIXED       -239041
      MMX_CAM-W2             MMX_SPACECRAFT         FIXED       -239042

      MMX_SHV_MSC            MMX_SPACECRAFT         FIXED       -239050
      MMX_SHV_SSC            MMX_SPACECRAFT         FIXED       -239051

      MMX_C-SMP_JT1_BASE     MMX_SPACECRAFT         FIXED       -239060
      MMX_C-SMP_JT1          MMX_C-SMP_JT1_BASE     CK          -239061
      MMX_C-SMP_JT2_BASE     MMX_C-SMP_JT1          FIXED       -239062
      MMX_C-SMP_JT2          MMX_C-SMP_JT2_BASE     CK          -239063
      MMX_C-SMP_JT3_BASE     MMX_C-SMP_JT2          FIXED       -239064
      MMX_C-SMP_JT3          MMX_C-SMP_JT3_BASE     CK          -239065
      MMX_C-SMP_JT4_BASE     MMX_C-SMP_JT3          FIXED       -239066
      MMX_C-SMP_JT4          MMX_C-SMP_JT4_BASE     CK          -239067
      MMX_C-SMP_JT5_BASE     MMX_C-SMP_JT4          FIXED       -239068
      MMX_C-SMP_JT5          MMX_C-SMP_JT5_BASE     CK          -239069
      MMX_C-SMP_HCAM         MMX_C-SMP_JT5          FIXED       -239070
      MMX_C-SMP_TMCAM        MMX_SPACECRAFT         FIXED       -239071
      MMX_P-SMP              MMX_SPACECRAFT         FIXED       -239072


   Science Instrument frames:
   --------------------------
      Name                   Relative to            Type        Frame ID
      ====================   ====================   =========   ========
      MMX_CMDM               MMX_SPACECRAFT         FIXED       -239100

      MMX_LIDAR_BASE         MMX_SPACECRAFT         FIXED       -239110
      MMX_LIDAR_TX           MMX_LIDAR_BASE         FIXED       -239111
      MMX_LIDAR_RX           MMX_LIDAR_BASE         FIXED       -239112

      MMX_MIRS               MMX_SPACECRAFT         FIXED       -239120
      MMX_MIRS_SCAN                                 SWITCH      -239121
      MMX_MIRS_SCAN_PLAN     MMX_MIRS               CK          -239122
      MMX_MIRS_SCAN_MEAS     MMX_MIRS               CK          -239123

      MMX_MEGANE_GRS         MMX_SPACECRAFT         FIXED       -239130
      MMX_MEGANE_NS          MMX_SPACECRAFT         FIXED       -239140

      MMX_MSA-S              MMX_SPACECRAFT         FIXED       -239150
      MMX_MSA_MG-S1          MMX_SPACECRAFT         FIXED       -239160
      MMX_MSA_MG-S2          MMX_SPACECRAFT         FIXED       -239170

      MMX_IREM               MMX_SPACECRAFT         FIXED       -239180

      MMX_TENGOO             MMX_SPACECRAFT         FIXED       -239190

      MMX_OROCHI_BASE        MMX_SPACECRAFT         FIXED       -239200
      MMX_OROCHI_390         MMX_OROCHI_BASE        FIXED       -239210
      MMX_OROCHI_480         MMX_OROCHI_BASE        FIXED       -239220
      MMX_OROCHI_550         MMX_OROCHI_BASE        FIXED       -239230
      MMX_OROCHI_650         MMX_OROCHI_BASE        FIXED       -239240
      MMX_OROCHI_730         MMX_OROCHI_BASE        FIXED       -239250
      MMX_OROCHI_860         MMX_OROCHI_BASE        FIXED       -239260
      MMX_OROCHI_950         MMX_OROCHI_BASE        FIXED       -239270
      MMX_OROCHI_VIS         MMX_OROCHI_BASE        FIXED       -239280
      MMX_OROCHI_LED         MMX_OROCHI_BASE        FIXED       -239290

      MMX_ROVER_NAVCAM-1     MMX_ROVER              FIXED       -2396xx
      MMX_ROVER_NAVCAM-2     MMX_ROVER              FIXED       -2396xx
      MMX_ROVER_WHEELCAM-1   MMX_ROVER              FIXED       -2396xx
      MMX_ROVER_WHEELCAM-2   MMX_ROVER              FIXED       -2396xx
      MMX_ROVER_RAX          MMX_ROVER              FIXED       -2396xx
      MMX_ROVER_MINIRAD      MMX_ROVER              FIXED       -2396xx


MMX Reference Frame Tree
------------------------------------------------------------------------------

   This diagram shows the MMX Reference frame tree:




                                J2000  INERTIAL (^)
   +--------------------------------------------------------+
   |     |         |     |       |         |                |
   |     |<-pck    |     |<-pck  |         |                |
   |     V         |     V       |         |                |
   | IAU_PHOBOS    | IAU_MARS    |         |                |
   | PHOBOS BFR(*) | MARS BFR(*) |         |                |
   | ------------- | ----------- |         |                |
   |               |             |         |                |
   |<-pck          |<-pck        |         |                |
   V               V             |         |                |
  IAU_EARTH       IAU_DEIMOS     |         |                |
  EARTH BFR(*)    DEIMOS BFR(*)  |         |                |
  ------------    -------------  |         |                |
                                 |         |                |
                             ck->|         |<-ck            |
                                 V         V                |
                  MMX_SPACECRAFT_PLAN   MMX_SPACECRAFT_MEAS |
                  -------------------   ------------------- |
                                 |         |                |
                                 |         |                |
            MMX_XMGA             +---------+       dynamic->|
            --------                  |                     V
                ^             switch->|            MMX_SAP_NOMINAL
        switch->|                     |            ---------------
                |                     |                |    |
           +---------+                |   MMX_SAP1     |    |     MMX_SAP2
           |         |                |   --------     |    |     --------
           |         |                |      ^         |    |         ^
   MMX_XMGA_PLAN  MMX_XMGA_MEAS       |      |<-switch |    | switch->|
   -------------  -------------       |      |         |    |         |
           ^         ^                |   +-----+      |    |      +-----+
       ck->|     ck->|                |   |     |  ck->|    |<-ck  |     |
           |         |                |   |     |      V    V      |     |
          MMX_XMGA_BASE               |   | MMX_SAP1_PLAN  MMX_SAP2_PLAN |
          -------------               |   | -------------  ------------- |
                ^                     |   |           ^      ^           |
                |<-fxd                |   |       ck->|      |<-ck       |
                |                     |   |           |      |           |
   MMX_XLGA-PZ  |  MMX_XLGA-PX        | MMX_SAP1_MEAS |      | MMX_SAP2_MEAS
   -----------  |  -----------        | ------------- |      | -------------
   ^            |  ^                  |     ^         |      |         ^
   |<-fxd       |  |<-fxd             |     |<-ck     |      |     ck->|
   |            |  |                  |     |         |      |         |
   | MMX_KAXHGA |  | MMX_XLGA-MX      |    MMX_SAP1_BASE    MMX_SAP2_BASE
   | ---------- |  | -----------      |    -------------    -------------
   |  ^         |  |  ^               |          ^                ^
   |  |<-fxd    |  |  |<-fxd          V          |<-fxd           |<-fxd
   |  |         |  |  |        MMX_SPACECRAFT    |                |
   +-------------------------------------------------------------------+
   |  |  |  |  |  |  |  |  |  |  |  |       |  |  |  |  |  |  |  |  |  |
   |  |  |  |  |  |  |  |  |  |  |  |<-fxd  |  |  |  |  |  |  |  |  |  |<-fxd
   |  |  |  |  |  |  |  |  |  |  |  V       |  |  |  |  |  |  |  |  |  V
   |  |  |  |  |  |  |  |  |  |  | MMX_ALT1 |  |  |  |  |  |  |  |  | MMX_IREM
   |  |  |  |  |  |  |  |  |  |  | -------- |  |  |  |  |  |  |  |  | --------
   |  |  |  |  |  |  |  |  |  |  |          |  |  |  |  |  |  |  |  |
   |  |  |  |  |  |  |  |  |  |  |<-fxd     |  |  |  |  |  |  |  |  |<-fxd
   |  |  |  |  |  |  |  |  |  |  V          |  |  |  |  |  |  |  |  V
   |  |  |  |  |  |  |  |  |  | MMX_ALT2    |  |  |  |  |  |  |  | MMX_SHV_MSC
   |  |  |  |  |  |  |  |  |  | --------    |  |  |  |  |  |  |  | -----------
   |  |  |  |  |  |  |  |  |  |             |  |  |  |  |  |  |  |
   |  |  |  |  |  |  |  |  |  |<-fxd        |  |  |  |  |  |  |  |<-fxd
   |  |  |  |  |  |  |  |  |  V             |  |  |  |  |  |  |  V
   |  |  |  |  |  |  |  |  | MMX_CMDM       |  |  |  |  |  |  | MMX_SHV_SSC
   |  |  |  |  |  |  |  |  | --------       |  |  |  |  |  |  | -----------
   |  |  |  |  |  |  |  |  |                |  |  |  |  |  |  |
   |  |  |  |  |  |  |  |  |<-fxd           |  |  |  |  |  |  |<-fxd
   |  |  |  |  |  |  |  |  V                |  |  |  |  |  |  V
   |  |  |  |  |  |  |  | MMX_CAM-T         |  |  |  |  |  | MMX_MSA-S
   |  |  |  |  |  |  |  | ---------         |  |  |  |  |  | ---------
   |  |  |  |  |  |  |  |                   |  |  |  |  |  |
   |  |  |  |  |  |  |  |<-fxd              |  |  |  |  |  |<-fxd
   |  |  |  |  |  |  |  V                   |  |  |  |  |  V
   |  |  |  |  |  |  | MMX_CAM-W1           |  |  |  |  | MMX_MSA_MG-S1
   |  |  |  |  |  |  | ----------           |  |  |  |  | -------------
   |  |  |  |  |  |  |                      |  |  |  |  |
   |  |  |  |  |  |  |<-fxd                 |  |  |  |  |<-fxd
   |  |  |  |  |  |  V                      |  |  |  |  V
   |  |  |  |  |  | MMX_CAM-W2              |  |  | MMX_MSA_MG-S2
   |  |  |  |  |  | ----------              |  |  | -------------
   |  |  |  |  |  |                         |  |  |
   |  |  |  |  |  |<-fxd                    |  |  |<-fxd
   |  |  |  |  |  V                         |  |  V
   |  |  |  |  | MMX_TENGOO                 |  | MMX_P-SMP
   |  |  |  |  | ----------                 |  | ---------
   |  |  |  |  |                            |  |
   |  |  |  |  |<-fxd                       |  |<-fxd
   |  |  |  |  V                            |  V
   |  |  |  | MMX_MEGANE_NS                 | MMX_C-SMP_TMCAM
   |  |  |  | -------------                 | ---------------
   |  |  |  |                               |
   |  |  |  |<-fxd                          |<-fxd
   |  |  |  V                               V
   |  |  | MMX_MEGANE_GRS                  MMX_MIRS
   |  |  | --------------                  --------
   |  |  |                                 |      |
   |  |  |<-fxd                            |<-ck  |<-ck
   |  |  V                                 V      V
   |  | MMX_LIDAR_BASE      MMX_MIRS_SCAN_PLAN  MMX_MIRS_SCAN_MEAS
   |  | --------------      ------------------  ------------------
   |  |  |           |                     |      |
   |  |  |<-fxd      |<-fxd                |      |
   |  |  V           V                     +------+
   |  | MMX_LIDAR_TX MMX_LIDAR_RX              |
   |  | ------------ ------------              |<-switch
   |  |                                        V
   |  |<-fxd                             MMX_MIRS_SCAN
   |  V                                  -------------
   |  MMX_OROCHI_BASE
   |  +-----------------------------------------------------+
   |  |   |   |              |   |   |              |   |   |
   |  |   |   |<-fxd         |   |   |<-fxd         |   |   |<-fxd
   |  |   |   V              |   |   V              |   |   V
   |  |   |  MMX_OROCHI_550  |   |  MMX_OROCHI_860  |   |  MMX_OROCHI_LED
   |  |   |  --------------  |   |  --------------  |   |  --------------
   |  |   |                  |   |                  |   |
   |  |   |<-fxd             |   |<-fxd             |   |<-fxd
   |  |   V                  |   V                  |   V
   |  |  MMX_OROCHI_480      |  MMX_OROCHI_730      |  MMX_OROCHI_VIS
   |  |  --------------      |  --------------      |  --------------
   |  |                      |                      |
   |  |<-fxd                 |<-fxd                 |<-fxd
   |  V                      V                      V
   | MMX_OROCHI_390         MMX_OROCHI_650         MMX_OROCHI_950
   | --------------         --------------         --------------
   |
   |<-fxd
   V
  MMX_C-SMP_JT1_BASE
  ------------------
   |
   |<-ck
   V
  MMX_C-SMP_JT1
  -------------
   |
   |<-fxd
   V
  MMX_C-SMP_JT2_BASE
  ------------------
   |
   |<-ck
   V
  MMX_C-SMP_JT2
  -------------
   |
   |<-fxd
   V
  MMX_C-SMP_JT3_BASE
  ------------------
   |
   |<-ck
   V
  MMX_C-SMP_JT3
  -------------
   |
   |<-fxd
   V
  MMX_C-SMP_JT4_BASE
  ------------------
   |
   |<-ck
   V
  MMX_C-SMP_JT4
  -------------
   |
   |<-fxd
   V
  MMX_C-SMP_JT5_BASE
  ------------------
   |
   |<-ck
   V
  MMX_C-SMP_JT5
  -------------
   |
   |<-fxd
   V
  MMX_C-SMP_HCAM
  --------------


   (*) BFR -- body-fixed rotating frame

   (^) The diagram does not show any dynamic frames except for
       MMX_SAP_NOMINAL, which are all defined w.r.t. J2000.


   This diagram shows the dynamic frames tree used in the MMX mission
   except for MMX_SAP_NOMINAL:

                  "J2000" INERTIAL
         +---------------------------------+
         |                 |               |
         |<-dynamic        |<-dynamic      |<-dynamic
         |                 |               |
         V                 V               |
    PHOBOS_MARS_P     DEIMOS_MARS_P        |
    -------------     -------------        |
         |                 |               |
         |<-dynamic        |<-dynamic      |
         |                 |               |
         |                 |               |
         V                 V               V
    MMX_PHOBOS_P      MMX_DEIMOS_P     MMX_MARS_P
    ------------      ------------     ----------



MMX Dynamic Frames Definitions
---------------------------------------------------------------------------

   The MMX_MARS_P, MMX_PHOBOS_P, and MMX_DEIMOS_P frames are defined for
   nominal orientation during Target Pointing Mode Mars (TPM-M), Phobos
   (TPM-P), and Deimos (TPM-D), respectively. The PHOBOS_MARS_P and
   DEIMOS_MARS_P are defined to be used for defining MMX_PHOBOS_P and
   MMX_DEIMOS_P frames, respectively.

   The PHOBOS_MARS_P frame is defined as follows [4]:

      - -X axis is along the geometric direction from Phobos to Mars;

      - +Y axis is along the velocity vector direction of PHOBOS in the
        IAU_MARS frame;

      - +Z axis completes the right-handed frame;

      - the origin of the frame is Mars' center of mass;

   This frame is defined as a two-vector style dynamic frame below.

      \begindata

         FRAME_PHOBOS_MARS_P          = -239910
         FRAME_-239910_NAME           = 'PHOBOS_MARS_P'
         FRAME_-239910_CLASS          = 5
         FRAME_-239910_CLASS_ID       = -239910
         FRAME_-239910_CENTER         = 499
         FRAME_-239910_RELATIVE       = 'J2000'
         FRAME_-239910_DEF_STYLE      = 'PARAMETERIZED'
         FRAME_-239910_FAMILY         = 'TWO-VECTOR'
         FRAME_-239910_PRI_AXIS       = '-X'
         FRAME_-239910_PRI_VECTOR_DEF = 'OBSERVER_TARGET_POSITION'
         FRAME_-239910_PRI_OBSERVER   = 'PHOBOS'
         FRAME_-239910_PRI_TARGET     = 'MARS'
         FRAME_-239910_PRI_ABCORR     = 'NONE'
         FRAME_-239910_SEC_AXIS       = 'Y'
         FRAME_-239910_SEC_VECTOR_DEF = 'OBSERVER_TARGET_VELOCITY'
         FRAME_-239910_SEC_OBSERVER   = 'PHOBOS'
         FRAME_-239910_SEC_TARGET     = 'MARS'
         FRAME_-239910_SEC_ABCORR     = 'NONE'
         FRAME_-239910_SEC_FRAME      = 'IAU_MARS'

      \begintext


   The DEIMOS_MARS_P frame is defined as follows [4]:

      - -X axis is along the geometric direction from Deimos to Mars;

      - +Y axis is along the velocity vector direction of Deimos in the
        IAU_MARS frame;

      - +Z axis completes the right-handed frame;

      - the origin of the frame is Mars' center of mass;

   This frame is defined as a two-vector style dynamic frame below.

      \begindata

         FRAME_DEIMOS_MARS_P          = -239911
         FRAME_-239911_NAME           = 'DEIMOS_MARS_P'
         FRAME_-239911_CLASS          = 5
         FRAME_-239911_CLASS_ID       = -239911
         FRAME_-239911_CENTER         = 499
         FRAME_-239911_RELATIVE       = 'J2000'
         FRAME_-239911_DEF_STYLE      = 'PARAMETERIZED'
         FRAME_-239911_FAMILY         = 'TWO-VECTOR'
         FRAME_-239911_PRI_AXIS       = '-X'
         FRAME_-239911_PRI_VECTOR_DEF = 'OBSERVER_TARGET_POSITION'
         FRAME_-239911_PRI_OBSERVER   = 'DEIMOS'
         FRAME_-239911_PRI_TARGET     = 'MARS'
         FRAME_-239911_PRI_ABCORR     = 'NONE'
         FRAME_-239911_SEC_AXIS       = 'Y'
         FRAME_-239911_SEC_VECTOR_DEF = 'OBSERVER_TARGET_VELOCITY'
         FRAME_-239911_SEC_OBSERVER   = 'DEIMOS'
         FRAME_-239911_SEC_TARGET     = 'MARS'
         FRAME_-239911_SEC_ABCORR     = 'NONE'
         FRAME_-239911_SEC_FRAME      = 'IAU_MARS'

      \begintext


   The MMX_MARS_P frame, representing the nominal Mars-pointed
   orientation, is defined as follows [4]:

      - -Z axis is along the geometric direction from the MMX spacecraft
        to Mars;

      - -X axis is along the velocity vector direction of MMX in the
        IAU_MARS frame;

      - +Y axis completes the right-handed frame;

      - the origin of the frame is at the center of Mars;

   This frame is defined as a two-vector style dynamic frame below.

      \begindata

         FRAME_MMX_MARS_P             = -239912
         FRAME_-239912_NAME           = 'MMX_MARS_P'
         FRAME_-239912_CLASS          = 5
         FRAME_-239912_CLASS_ID       = -239912
         FRAME_-239912_CENTER         = 499
         FRAME_-239912_RELATIVE       = 'J2000'
         FRAME_-239912_DEF_STYLE      = 'PARAMETERIZED'
         FRAME_-239912_FAMILY         = 'TWO-VECTOR'
         FRAME_-239912_PRI_AXIS       = '-Z'
         FRAME_-239912_PRI_VECTOR_DEF = 'OBSERVER_TARGET_POSITION'
         FRAME_-239912_PRI_OBSERVER   = 'PHOBOS'
         FRAME_-239912_PRI_TARGET     = 'MARS'
         FRAME_-239912_PRI_ABCORR     = 'NONE'
         FRAME_-239912_SEC_AXIS       = 'X'
         FRAME_-239912_SEC_VECTOR_DEF = 'OBSERVER_TARGET_VELOCITY'
         FRAME_-239912_SEC_OBSERVER   = 'MMX'
         FRAME_-239912_SEC_TARGET     = 'MARS'
         FRAME_-239912_SEC_ABCORR     = 'NONE'
         FRAME_-239912_SEC_FRAME      = 'IAU_MARS'

     \begintext


   The MMX_PHOBOS_P frame, representing the nominal Phobos-pointed
   orientation which is useful during Target Pointing Mode Phobos (TPM-P),
   is defined as follows [4]:

      - -Z axis is along the geometric direction from the MMX spacecraft
        to Phobos;

      - -Y axis is as close as possible to the +Z-axis of PHOBOS_MARS_P
        frame;

      - +X axis completes the right-handed frame;

      - the origin of the frame is at the center of Mars;

   This frame is defined as a two-vector style dynamic frame below.

      \begindata

         FRAME_MMX_PHOBOS_P           = -239913
         FRAME_-239913_NAME           = 'MMX_PHOBOS_P'
         FRAME_-239913_CLASS          = 5
         FRAME_-239913_CLASS_ID       = -239913
         FRAME_-239913_CENTER         = 499
         FRAME_-239913_RELATIVE       = 'J2000'
         FRAME_-239913_DEF_STYLE      = 'PARAMETERIZED'
         FRAME_-239913_FAMILY         = 'TWO-VECTOR'
         FRAME_-239913_PRI_AXIS       = '-Z'
         FRAME_-239913_PRI_VECTOR_DEF = 'OBSERVER_TARGET_POSITION'
         FRAME_-239913_PRI_OBSERVER   = -239
         FRAME_-239913_PRI_TARGET     = 'PHOBOS'
         FRAME_-239913_PRI_ABCORR     = 'NONE'
         FRAME_-239913_SEC_AXIS       = '-Y'
         FRAME_-239913_SEC_VECTOR_DEF = 'CONSTANT'
         FRAME_-239913_SEC_SPEC       = 'RECTANGULAR'
         FRAME_-239913_SEC_VECTOR     = ( 0.0, 0.0, 1.0 )
         FRAME_-239913_SEC_FRAME      = 'PHOBOS_MARS_P'

     \begintext


   The MMX_DEIMOS_P frame, representing the nominal Deimos-pointed
   orientation, is defined as follows [4]:

      - -Z axis is along the geometric direction from the MMX spacecraft
        to Deimos;

      - -Y axis is as close as possible to the +Z-axis of DEIMOS_MARS_P
        frame;

      - +X axis completes the right-handed frame;

      - the origin of the frame is at the center of Mars;

   This frame is defined as a two-vector style dynamic frame below.

      \begindata

         FRAME_MMX_DEIMOS_P           = -239914
         FRAME_-239914_NAME           = 'MMX_DEIMOS_P'
         FRAME_-239914_CLASS          = 5
         FRAME_-239914_CLASS_ID       = -239914
         FRAME_-239914_CENTER         = 499
         FRAME_-239914_RELATIVE       = 'J2000'
         FRAME_-239914_DEF_STYLE      = 'PARAMETERIZED'
         FRAME_-239914_FAMILY         = 'TWO-VECTOR'
         FRAME_-239914_PRI_AXIS       = '-Z'
         FRAME_-239914_PRI_VECTOR_DEF = 'OBSERVER_TARGET_POSITION'
         FRAME_-239914_PRI_OBSERVER   = -239
         FRAME_-239914_PRI_TARGET     = 'DEIMOS'
         FRAME_-239914_PRI_ABCORR     = 'NONE'
         FRAME_-239914_SEC_AXIS       = '-Y'
         FRAME_-239914_SEC_VECTOR_DEF = 'CONSTANT'
         FRAME_-239914_SEC_SPEC       = 'RECTANGULAR'
         FRAME_-239914_SEC_VECTOR     = ( 0.0, 0.0, 1.0 )
         FRAME_-239914_SEC_FRAME      = 'DEIMOS_MARS_P'

     \begintext


MMX Spacecraft Frame Definition
---------------------------------------------------------------------------

   The MMX spacecraft consists of three modules: the propulsion module, the
   exploration module, and the return module. The propulsion module will be
   released after the Mars Orbit Insertion (MOI), and the exploration
   module will be released before leaving the Martian system. Only the
   return module will be back to the Earth.

   The MMX spacecraft frame, MMX_SPACECRAFT, is defined as follows [17]:

      - +X axis is parallel to a direction of the Earth pointing surface;

      - +Y axis is parallel to the solar array paddles direction;

      - +Z axis completes the right-handed frame;

      - the origin of the frame is intersection point between a spacecraft
        center line and the separation plane of the propulsion module
        and the return module.

   The MMX spacecraft frame is shown on the following diagrams with and
   without the propulsion module:


  S/C -X side view:
  -----------------

                               _               _
                              | |.-----------.| |
                              \ /|   .---.   |\ /
                              _v |   |   |   | v_
 +-------------------+       |  ||   |   |   ||  |       +-------------------+
 |                   |       |  ||   |   |   ||  |       |                   |
 |                   |       |__||   |   |   ||__|       |                   |
 |                   |       _   |   |  +Zsc |  _        |                   |
 |                   |      | |  |   | ^ |   | | |       |                   |
 +-------------------+      \ /  |   `-|-'   | \ /       +-------------------+
 +-------------------+    ___v___|__<--x_____|__v____    +-------------------+
 |                   |   |       | +Ysc      |       |   |                   |
 |       SAP1        |---|  SSC  |           | CMDM  |---|       SAP2        |
 |                   |---|       |           |       |---|                   |
 |                   |   |  .----------^-----+      _|   |                   |
 +-------------------+   +-'    .'   'SRC`   `.____|\    +-------------------+
 +-------------------+    ||--.'-----`._.'-----`.-----   +-------------------+
 |                   |      .'   _.-'     `-._   `. -=   |                   |
 |                   |    .'  _.'             `_.  `.    |                   |
 |                   |  .' .-'                   `-. `.  |                   |
 |                   | ---'                         `--- |                   |
 +-------------------+                                   +-------------------+



  S/C -X side view without the propulsion module:
  -----------------------------------------------

 +-------------------+                                   +-------------------+
 |                   |                                   |                   |
 |                   |                                   |                   |
 |                   |                  +Zsc             |                   |
 |                   |      ___        ^       ___       |                   |
 +-------------------+      \ /      .-|-.     \ /       +-------------------+
 +-------------------+    ___v______<--x__`_____v____    +-------------------+
 |                   |   |       | +Ysc      |       |   |                   |
 |       SAP1        |---|  SSC  |           | CMDM  |---|       SAP2        |
 |                   |---|       |           |       |---|                   |
 |                   |   |  .----------^-----+      _|   |                   |
 +-------------------+   +-'    .'   'SRC`   `.____|\    +-------------------+
 +-------------------+    ||--.'-----`._.'-----`.-----   +-------------------+
 |                   |      .'   _.-'     `-._   `. -=   |                   |
 |                   |    .'  _.'             `_.  `.    |                   |
 |                   |  .' .-'                   `-. `.  |                   |
 |                   | ---'                         `--- |                   |
 +-------------------+                                   +-------------------+



  S/C -Z side ("bottom") view with the exploration module:
  --------------------------------------------------------

        _____                                                          _____
       /     \                                                        /     \
      /       \                          __                          /       \
      \       `-._                      |  |MSA-S                 _.-'       /
       \____\\``  `-._      ___________/|  |                  _.-'  ''//____/
             \\ ``    `-._  ---------------|------------  _.-'    '' //
              \\  ``      `-._         .'  `.         _.-'      ''  //
               \\   ``        `-._   .'      `.   _.-'        ''   //
                \\    ``          `.'          `.'          ''    //
   SAP2         _\\     ``     o ALT1            `. o ALT2''     //_      SAP1
   ------------|  \\      ``   .'     ------.      `.   ''      //  |---------
               |   \\      CAM-W1 _  | Rover|        `''       //   |
               |    \\ TENGOO  _ |_| |      |        __`.     //    |
               |CAM-T\\   .--.|_|    |______|       |   |`.  //     |
               | .--. \\.'|  | CAM-W2    ^          |___|  `//      |
               | |  |  \\ `--'           |+Xsc     OROCHI  //`. __  |
               | `--'   \\               |                //   |  | |
     MEGANE GRS|==           MEGANE NS   x--->                 |MIRS|
               |_____   //                 +Ysc           \\   |__| |
               |     `.//         +Zsc is                  \\.'     |
               |      //.         into the   C-SMP         .\\      |
               |     //  `. LIDAR   page                 .'  \\     |
               |    //     `.---.                      .'     \\    |
               |   //       |   |                    .'        \\   |
               |_ //       ''---                   .' ``        \\ _|
                 //      ''      `.              .'     ``       \\
                //     ''          `_.-'    `-._'         ``      \\
               //    ''         _.-' ---------- `-._        ``     \\
              //   ''       _.-'     |        |     `-._      ``    \\
         ____//  ''     _.-'         |        |         `-._    ``   \\_____
        /   //\''   _.-'             |        | ___         `-._  ``  \\    \
       /       \_.-'                _|        ||_o_|            `-._``       \
       \       /                    |_        _|   MSC               \       /
        \_____/                       `|____.'SRC                     \_____/




   The spacecraft attitude is provided by a Switch Frame aligned with
   one of the different CK-based frames (MMX_SPACECRAFT_PLAN, or
   MMX_SPACECRAFT_MEAS) depending on coverage. MMX_SPACECRAFT_MEAS has
   priority over MMX_SPACECRAFT_PLAN whenever coverage for both is
   available.

      \begindata

         FRAME_MMX_SPACECRAFT       = -239000
         FRAME_-239000_NAME         = 'MMX_SPACECRAFT'
         FRAME_-239000_CLASS        = 6
         FRAME_-239000_CLASS_ID     = -239000
         FRAME_-239000_CENTER       = -239
         FRAME_-239000_ALIGNED_WITH = (
                                        'MMX_SPACECRAFT_PLAN'
                                        'MMX_SPACECRAFT_MEAS'
                                      )

      \begintext

   The MMX spacecraft planning reference frame -- MMX_SPACECRAFT_PLAN --
   is defined in order to accommodate the C-kernels that have been
   generated with a fictional SCLK kernel. These CK kernels contain
   predicted and test data and are used for planning purposes.

   The before-mentioned CKs are generated with a fictional SCLK kernel
   due to the fact that successive updates of the real SCLK kernel would
   lead to erroneous results for the predicted data provided by those
   kernels after the last Time Correlation Packet offered by the real
   SCLK.

   Since the spacecraft predicted attitude is defined with respect to
   an inertial frame and provided by a C-kernel (see [3] for more
   information), this frame is defined as a CK-based frame. These sets
   of keywords define the MMX_SPACECRAFT_PLAN frame.

      \begindata

         FRAME_MMX_SPACECRAFT_PLAN = -239001
         FRAME_-239001_NAME        = 'MMX_SPACECRAFT_PLAN'
         FRAME_-239001_CLASS       = 3
         FRAME_-239001_CLASS_ID    = -239001
         FRAME_-239001_CENTER      = -239
         CK_-239001_SCLK           = -239999
         CK_-239001_SPK            = -239

      \begintext

   The MMX spacecraft measured reference frame -- MMX_SPACECRAFT_MEAS --
   is defined in order to accommodate the C-kernels that have been
   generated with a real SCLK kernel. These C-kernels contain measured
   data from the housekeeping telemetry and are mainly used for data
   analysis.

   Since the spacecraft measured attitude is defined with respect to an
   inertial frame and provided by a C-kernel (see [3] for more information),
   this frame is defined as a CK-based frame.

      \begindata

         FRAME_MMX_SPACECRAFT_MEAS = -239002
         FRAME_-239002_NAME        = 'MMX_SPACECRAFT_MEAS'
         FRAME_-239002_CLASS       = 3
         FRAME_-239002_CLASS_ID    = -239002
         FRAME_-239002_CENTER      = -239
         CK_-239002_SCLK           = -239
         CK_-239002_SPK            = -239

      \begintext


MMX Spacecraft Bus Frames
---------------------------------------------------------------------------

   This section contains frame definitions for the MMX spacecraft bus.

   The frames are defined as fixed offset frames with their orientation
   specified using Euler angles.

   Note that angles in the frame definitions are specified for
   "from instrument to base (relative to) frame" transformation.


Solar Array Paddle Frames definition
-------------------------------------

   In this section, the antenna frames -- MMX_SAP1_BASE, MMX_SAP2_BASE,
   MMX_SAP1, MMX_SAP2, MMX_SAP_NOMINAL -- frames will be defined.

   The Solar Array Paddle 1 (SAP1) Base frame -- MMX_SAP1_BASE -- is
   defined as follows [17]:

      - +X axis is nominally co-aligned with the s/c -Z axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis;

      - +Z axis is nominally co-aligned with the s/c +X axis and
        completes the right hand frame;

      - the origin of the frame is at an intersection point between
        a SAP1 and a Solar Array Drive Mechanism 1 (SADM1) connection
        plane and a rotating axis of SADM1;

   The Solar Array Paddle 2 (SAP2) Base frame -- MMX_SAP2_BASE -- is
   defined as follows [17]:

      - +X axis is nominally co-aligned with the s/c +Z axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis;

      - +Z axis is nominally co-aligned with the s/c -X axis and
        completes the right hand frame;

      - the origin of the frame is at an intersection point between
        a SAP2 and a Solar Array Drive Mechanism 2 (SADM2) connection
        plane and a rotating axis of SADM2;

   The Solar Array Paddle 1 (SAP1) frame -- MMX_SAP1 -- is defined as
   follows [17]:

      - +Z axis is normal to the array surface on the active cell side
        and is co-aligned with the +Z axis of the SAP1 base frame when
        the paddle angle is zero;

      - +Y axis is nominally co-aligned with the +Y axis of the SAP1
        base frame, MMX_SAP1_BASE;

      - +X axis is co-aligned with the +X axis of the SAP1 base frame,
        MMX_SAP1_BASE, when the paddle angle is zero, and it completes
        the right hand frame;

      - the origin of the frame is at the center of the active cell of
        the array surface;

   The Solar Array Paddle 2 (SAP2) frame -- MMX_SAP2 -- is defined as
   follows [17]:

      - +Z axis is normal to the array surface on the active cell side
        and is co-aligned with the +Z axis of the SAP2 base frame,
        MMX_SAP2_BASE, when the paddle angle is zero;

      - +Y axis is nominally co-aligned with the +Y axis of the SAP2
        base frame, MMX_SAP2_BASE;

      - +X axis is co-aligned with the +X axis of the SAP2 base frame,
        MMX_SAP2_BASE, when the paddle angle is zero, and it completes
        the right hand frame;

      - the origin of the frame is at the center of the active cell of
        the array surface;


   The solar array paddle 1 (SAP1) orientation is provided by a Switch
   Frame aligned with one of the different CK-based frames (MMX_SAP1_PLAN,
   or MMX_SAP1_MEAS) depending on coverage. MMX_SAP1_MEAS has priority over
   MMX_SAP1_PLAN whenever coverage for both is available.

   The solar array paddle 2 (SAP2) orientation is provided by a Switch
   Frame aligned with one of the different CK-based frames (MMX_SAP2_PLAN,
   or MMX_SAP2_MEAS) depending on coverage. MMX_SAP2_MEAS has priority over
   MMX_SAP2_PLAN whenever coverage for both is available.


      \begindata

         FRAME_MMX_SAP1             = -239011
         FRAME_-239011_NAME         = 'MMX_SAP1'
         FRAME_-239011_CLASS        = 6
         FRAME_-239011_CLASS_ID     = -239011
         FRAME_-239011_CENTER       = -239
         FRAME_-239011_ALIGNED_WITH = (
                                        'MMX_SAP1_PLAN',
                                        'MMX_SAP1_MEAS'
                                      )

         FRAME_MMX_SAP2             = -239015
         FRAME_-239015_NAME         = 'MMX_SAP2'
         FRAME_-239015_CLASS        = 6
         FRAME_-239015_CLASS_ID     = -239015
         FRAME_-239015_CENTER       = -239
         FRAME_-239015_ALIGNED_WITH = (
                                        'MMX_SAP2_PLAN',
                                        'MMX_SAP2_MEAS'
                                      )

      \begintext

   The MMX Solar Array Paddle 1 planning frame -- MMX_SAP1_PLAN -- and
   the MMX Solar Array Paddle 2 planning frame -- MMX_SAP2_PLAN -- are
   defined in order to accommodate the C-kernels that have been generated
   with a fictional SCLK kernel. These CK kernels contain predicted and
   test data and are used for planning purposes.

   The before-mentioned CKs are generated with a fictional SCLK kernel
   due to the fact that successive updates of the real SCLK kernel would
   lead to erroneous results for the predicted data provided by those
   kernels after the last Time Correlation Packet offered by the real
   SCLK.

   Since the spacecraft predicted attitude is defined with respect to
   an inertial frame and provided by a C-kernel (see [3] for more
   information), these frames are defined as a CK-based frame. These sets
   of keywords define the MMX_SAP1_PLAN and MMX_SAP2_PLAN frames.

      \begindata

         FRAME_MMX_SAP1_PLAN      = -239012
         FRAME_-239012_NAME       = 'MMX_SAP1_PLAN'
         FRAME_-239012_CLASS      = 3
         FRAME_-239012_CLASS_ID   = -239012
         FRAME_-239012_CENTER     = -239
         CK_-239012_SCLK          = -239999
         CK_-239012_SPK           = -239

         FRAME_MMX_SAP2_PLAN      = -239016
         FRAME_-239016_NAME       = 'MMX_SAP2_PLAN'
         FRAME_-239016_CLASS      = 3
         FRAME_-239016_CLASS_ID   = -239016
         FRAME_-239016_CENTER     = -239
         CK_-239016_SCLK          = -239999
         CK_-239016_SPK           = -239

      \begintext

   The MMX Solar Array Paddle 1 measured frame and the MMX Solar Array
   Paddle 2 measured frame -- MMX_SAP1_MEAS and MMX_SAP2_MEAS, respectively
   -- are defined in order to accommodate the C-kernels that have been
   generated with a real SCLK kernel. These C-kernels contain measured data
   from the housekeeping telemetry and are mainly used for data analysis.

   Since the solar array paddle measured orientations are defined with
   respect to the Solar Array Paddle 1 (SAP1) Base frame or the Solar
   Array Paddle 2 (SAP2) Base frame and provided by a C-kernel (see [3]
   for more information), these frames are defined as a CK-based frame.

      \begindata

         FRAME_MMX_SAP1_MEAS      = -239013
         FRAME_-239013_NAME       = 'MMX_SAP1_MEAS'
         FRAME_-239013_CLASS      = 3
         FRAME_-239013_CLASS_ID   = -239013
         FRAME_-239013_CENTER     = -239
         CK_-239013_SCLK          = -239
         CK_-239013_SPK           = -239

         FRAME_MMX_SAP2_MEAS      = -239017
         FRAME_-239017_NAME       = 'MMX_SAP2_MEAS'
         FRAME_-239017_CLASS      = 3
         FRAME_-239017_CLASS_ID   = -239017
         FRAME_-239017_CENTER     = -239
         CK_-239017_SCLK          = -239
         CK_-239017_SPK           = -239

      \begintext

      \begindata

         FRAME_MMX_SAP1_BASE      = -239010
         FRAME_-239010_NAME       = 'MMX_SAP1_BASE'
         FRAME_-239010_CLASS      = 4
         FRAME_-239010_CLASS_ID   = -239010
         FRAME_-239010_CENTER     = -239
         TKFRAME_-239010_SPEC     = 'ANGLES'
         TKFRAME_-239010_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239010_ANGLES   = (  -90.0     0.0      0.0 )
         TKFRAME_-239010_AXES     = (    2       1        3   )
         TKFRAME_-239010_UNITS    = 'DEGREES'

         FRAME_MMX_SAP2_BASE      = -239014
         FRAME_-239014_NAME       = 'MMX_SAP2_BASE'
         FRAME_-239014_CLASS      = 4
         FRAME_-239014_CLASS_ID   = -239014
         FRAME_-239014_CENTER     = -239
         TKFRAME_-239014_SPEC     = 'ANGLES'
         TKFRAME_-239014_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239014_ANGLES   = (   90.0     0.0      0.0 )
         TKFRAME_-239014_AXES     = (    2       1        1   )
         TKFRAME_-239014_UNITS    = 'DEGREES'

      \begintext


Antenna Frames definition
-------------------------

In this section, the antenna frames -- MMX_KAXHGA, MMX_XMGA_BASE,
MMX_XMGA, MMX_XLGA-PX, MMX_XLGA-PZ, MMX_XLGA-MX -- will be defined.

   The Ka- and X- bands High-gain Antenna frame -- MMX_KAXHGA -- is
   defined as follows [17]:

      - +Z axis is along the boresight direction, and is co-aligned
        with the s/c +X axis;

      - +X axis is nominally co-aligned with the s/c +Y axis;

      - +Y axis is nominally co-aligned with the s/c +Z axis and it
        completes the right hand frame;

      - the origin of the frame is at the focal point of the antenna;


   The X-band Medium-gain Antenna base frame -- MMX_XMGA_BASE -- is
   defined as follows [17]:

      - +Y axis is nominally co-aligned with the s/c +Y axis;

      - +X axis is rotated 11 degrees around the s/c +Y axis from the
        s/c +X axis;

      - +Z axis is rotated 11 degrees around the s/c +Y axis from the
        s/c +Z axis and it completes the right hand frame;

      - the origin of the frame is at the gimbal of the antenna;


   The X-band Medium-gain Antenna frame -- MMX_XMGA -- is defined
   as follows [17]:

      - +Z axis is along the boresight direction of the antenna and
        is co-aligned with the Z axis of the XMGA base frame when the
        XMGA is at zero degrees position around LR axis and FB axis;

      - +X axis is perpendicular to the +Z axis and is co-aligned with
        the +X axis of the XMGA base frame when the XMGA is at zero
        degrees position around LR axis and FB axis;

      - +Y axis is perpendicular to the +Z axis and is co-aligned with
        the +Y axis of the XMGA base frame when the XMGA is at zero
        degrees position around LR axis and FB axis and it completes
        the right hand frame;

      - the origin of the frame is at the focal point of the antenna;


   The +X-pointing Low-gain Antenna frame -- MMX_XLGA-PX -- is defined
   as follows [17]:

      - +Z axis is along the boresight of antenna and is nominally
        co-aligned with the s/c +X axis;

      - +X axis is nominally co-aligned with the s/c -Z axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis and it
        completes the right hand frame;

      - the origin of the frame is at an mounting reference point of
        the antenna.


   MMX_XLGA-PZ and MMX_XLGA-MX will be defined later.

      \begindata

         FRAME_MMX_KAHGA_BASE     = -239020
         FRAME_-239020_NAME       = 'MMX_KAHGA'
         FRAME_-239020_CLASS      = 4
         FRAME_-239020_CLASS_ID   = -239020
         FRAME_-239020_CENTER     = -239
         TKFRAME_-239020_SPEC     = 'ANGLES'
         TKFRAME_-239020_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239020_ANGLES   = (  -90.0   -90.0      0.0 )
         TKFRAME_-239020_AXES     = (    2       1        3   )
         TKFRAME_-239020_UNITS    = 'DEGREES'

         FRAME_MMX_XLGA-PX        = -239021
         FRAME_-239021_NAME       = 'MMX_XLGA-PX'
         FRAME_-239021_CLASS      = 4
         FRAME_-239021_CLASS_ID   = -239021
         FRAME_-239021_CENTER     = -239
         TKFRAME_-239021_SPEC     = 'ANGLES'
         TKFRAME_-239021_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239021_ANGLES   = (    0.0     0.0      0.0 )
         TKFRAME_-239021_AXES     = (    1       1        3   )
         TKFRAME_-239021_UNITS    = 'DEGREES'

         FRAME_MMX_XMGA_BASE      = -239024
         FRAME_-239024_NAME       = 'MMX_XMGA_BASE'
         FRAME_-239024_CLASS      = 4
         FRAME_-239024_CLASS_ID   = -239024
         FRAME_-239024_CENTER     = -239
         TKFRAME_-239024_SPEC     = 'ANGLES'
         TKFRAME_-239024_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239024_ANGLES   = (  -11.0     0.0      0.0 )
         TKFRAME_-239024_AXES     = (    2       1        3   )
         TKFRAME_-239024_UNITS    = 'DEGREES'

      \begintext


   The X-band Medium-gain Antenna orientation is provided by a Switch
   Frame aligned with one of the different CK-based frames (MMX_XMGA_PLAN,
   or MMX_XMGA_MEAS) depending on coverage. MMX_XMGA_MEAS has priority over
   MMX_XMGA_PLAN whenever coverage for both is available.

      \begindata

         FRAME_MMX_XMGA             = -239025
         FRAME_-239025_NAME         = 'MMX_XMGA'
         FRAME_-239025_CLASS        = 6
         FRAME_-239025_CLASS_ID     = -239025
         FRAME_-239025_CENTER       = -239
         FRAME_-239025_ALIGNED_WITH = (
                                        'MMX_XMGA_PLAN',
                                        'MMX_XMGA_MEAS'
                                      )

      \begintext

   The MMX X-band Medium-gain Antenna planning frame -- MMX_XMGA_PLAN --
   is defined in order to accommodate the C-kernels that have been
   generated with a fictional SCLK kernel. These CK kernels contain
   predicted and test data and are used for planning purposes.

   The before-mentioned CKs are generated with a fictional SCLK kernel
   due to the fact that successive updates of the real SCLK kernel would
   lead to erroneous results for the predicted data provided by those
   kernels after the last Time Correlation Packet offered by the real
   SCLK.

   Since the spacecraft predicted attitude is defined with respect to
   an inertial frame and provided by a C-kernel (see [3] for more
   information), this frame is defined as a CK-based frame. These sets
   of keywords define the MMX_XMGA_PLAN frame.

      \begindata

         FRAME_MMX_XMGA_PLAN       = -239026
         FRAME_-239026_NAME        = 'MMX_XMGA_PLAN'
         FRAME_-239026_CLASS       = 3
         FRAME_-239026_CLASS_ID    = -239026
         FRAME_-239026_CENTER      = -239
         CK_-239026_SCLK           = -239999
         CK_-239026_SPK            = -239

      \begintext

   The MMX X-band Medium-gain Antenna measured frame -- MMX_XMGA_MEAS --
   is defined in order to accommodate the C-kernels that have been
   generated with a real SCLK kernel. These C-kernels contain measured
   data from the housekeeping telemetry and are mainly used for data
   analysis.

   Since the X-band Medium-gain Antenna measured orientation is defined
   with respect to the X-band Medium-gain Antenna Base frame and provided
   by a C-kernel (see [3] for more information), this frame is defined as
   a CK-based frame.

      \begindata

         FRAME_MMX_XMGA_MEAS       = -239027
         FRAME_-239027_NAME        = 'MMX_XMGA_MEAS'
         FRAME_-239027_CLASS       = 3
         FRAME_-239027_CLASS_ID    = -239027
         FRAME_-239027_CENTER      = -239
         CK_-239027_SCLK           = -239
         CK_-239027_SPK            = -239

      \begintext


Altimeter Frames definition
---------------------------

In this section, the altimeter frames -- MMX_ALT1 and MMX_ALT2 --
will be defined.

   The Altimeter 1 frame -- MMX_ALT1 -- is defined as follows [17]:

      - +X axis is rotated 45 degrees from the s/c +X direction to
        the s/c -Y direction;

      - +Y axis is rotated 135 degrees from the s/c +Y direction to
        the s/c +X direction;

      - +Z axis is co-aligned with the s/c -Z axis and completes the
        right hand frame;

      - the origin of the frame is TBD.


   The Altimeter 2 frame -- MMX_ALT2 -- is defined as follows [17]:

      - +X axis is rotated 135 degrees from the s/c +X direction to
        the s/c +Y direction;

      - +Y axis is rotated 45 degrees from the s/c +Y direction to
        the s/c +X direction;

      - +Z axis is co-aligned with the s/c -Z axis and completes the
        right hand frame;

      - the origin of the frame is TBD.




Navigation Camera Frames definition
-----------------------------------

In this section, the navigation camera frames -- MMX_CAM-T,
MMX_CAM-W1, and MMX_CAM-W2 -- are defined.

   The CAM-T frame -- MMX_CAM-T -- is defined as follows [16]:

      - -Z axis is along the boresight direction of the CAM-T and
        almost co-aligned with the s/c -Z axis;
        -Z axis is tilted from the s/c -Z axis at 0.48 degree in the
        55.8 degree clockwise azimuth direction from the s/c X axis
        around the s/c -Z axis;

      - +X axis is almost co-aligned with the s/c +X axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is at the focal point of the CAM-T
        optics;

   The CAM-T instrument is on the -Z panel of the spacecraft with
   approximately -Z direction field of view of the spacecraft.


   The CAM-W frames -- MMX_CAM-W1 and MMX_CAM-W2 -- is defined as follows [16]:

      - +X axis is nominally co-aligned with the s/c +Y axis;

      - +Y axis is nominally co-aligned with the s/c +X axis;

      - +Z axis is nominally co-aligned with the s/c -Z axis and completes the
        right hand frame;

      - the origin of the frame is at the focal point of optics of
        CAM-W1 and CAM-W2, respectively;


   S/C -Z side ("bottom") view with the exploration module:
   --------------------------------------------------------
        _____                                                          _____
       /     \                                                        /     \
      /       \                          __                          /       \
      \       `-._                      |  |                      _.-'       /
       \____\\``  `-._      ___________/|  |                  _.-'  ''//____/
             \\ ``    `-._  ---------------|------------  _.-'    '' //
              \\  ``      `-._         .'  `.         _.-'      ''  //
               \\   ``        `-._   .'      `.   _.-'        ''   //
                \\    ``          `.'          `.'          ''    //
   SAP          _\\     ``       .^ +Ycamw2      `.       ''     //_      SAP
   ------------|  \\      ``   .' |     _____      `.   ''      //  |---------
               |   \\       ``'^  o--> |     |       `''       //   |
               |    \\  +Ycamw1|    +Xcamw2  |       __`.     //    |
           +Xcamt ^  \\   .--. o-->    |_____|      |   |`.  //     |
               | .|-. \\.'|  |  +Xcamw1             |___|  `//      |
               | |x--> \\ `--'           ^+Xsc             //`. __  |
               | `--'   \\               |                //   |  | |
    +Zsc and   |== +Ycamt                x--->                 |  | |
    +Zcamt are |_____   //                 +Ysc           \\   |__| |
    into the   |     `.//                                  \\.'     |
    page       |      //.                                  .\\      |
               |     //  `.                              .'  \\     |
               |    //     `.---.                      .'     \\    |
               |   //       |   |                    .'        \\   |
               |_ //       ''---                   .' ``        \\ _|
                 //      ''      `.              .'     ``       \\
                //     ''          `_.-'    `-._'         ``      \\
               //    ''         _.-' ---------- `-._        ``     \\
              //   ''       _.-'     |        |     `-._      ``    \\
         ____//  ''     _.-'         |        |         `-._    ``   \\_____
        /   //\''   _.-'             |        | ___         `-._  ``  \\    \
       /       \_.-'                _|        ||_o_|            `-._``       \
       \       /                    |_        _|                     \       /
        \_____/                       `|____.'                        \_____/



      \begindata

         FRAME_MMX_CAM-T          = -239040
         FRAME_-239040_NAME       = 'MMX_CAM-T'
         FRAME_-239040_CLASS      = 4
         FRAME_-239040_CLASS_ID   = -239040
         FRAME_-239040_CENTER     = -239
         TKFRAME_-239040_SPEC     = 'ANGLES'
         TKFRAME_-239040_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239040_ANGLES   = (  -55.8     0.48    55.8 )
         TKFRAME_-239040_AXES     = (    3       2        3   )
         TKFRAME_-239040_UNITS    = 'DEGREES'

         FRAME_MMX_CAM-W1         = -239041
         FRAME_-239041_NAME       = 'MMX_CAM-W1'
         FRAME_-239041_CLASS      = 4
         FRAME_-239041_CLASS_ID   = -239041
         FRAME_-239041_CENTER     = -239
         TKFRAME_-239041_SPEC     = 'ANGLES'
         TKFRAME_-239041_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239041_ANGLES   = (   90.0     0.0    180.0 )
         TKFRAME_-239041_AXES     = (    3       2        1   )
         TKFRAME_-239041_UNITS    = 'DEGREES'

         FRAME_MMX_CAM-W2         = -239042
         FRAME_-239042_NAME       = 'MMX_CAM-W2'
         FRAME_-239042_CLASS      = 4
         FRAME_-239042_CLASS_ID   = -239042
         FRAME_-239042_CENTER     = -239
         TKFRAME_-239042_SPEC     = 'ANGLES'
         TKFRAME_-239042_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239042_ANGLES   = (   90.0     0.0    180.0 )
         TKFRAME_-239042_AXES     = (    3       2        1   )
         TKFRAME_-239042_UNITS    = 'DEGREES'

      \begintext


Super High-Vision Camera Frames definition
------------------------------------------

   Super High-Vision Camera (SHV) consists of two cameras, Main SHV
   Camera (MSC) and Side SHV Camera (SSC) [5,6].

   The SHV MSC frame -- MMX_SHV_MSC -- is defined as follows:

      - -Z axis is along the boresight direction of the MSC and
        rotated 3 degrees about the s/c +Y axis from the s/c -Z
        axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis;

      - +X axis completes the right hand frame;

      - the origin of the frame is at the focal point of MSC optics.


   The SHV SSC frame -- MMX_SHV_SSC -- is defined as follows:

      - -X axis is along the boresight direction of SSC and
        nominally co-aligned with the s/c -X axis;

      - +Y axis is nominally co-aligned with the s/c -Y axis;

      - +Z axis is nominally co-aligned with the s/c -Z axis and
        completes the right hand frame;

      - the origin of the frame is at the focal point of SSC optics.


  S/C -X side view without the propulsion module:
  -----------------------------------------------

 +-------------------+                                   +-------------------+
 |                   |                                   |                   |
 |                   |                                   |                   |
 |                   |                                   |                   |
 |                   |      ___                ___       |                   |
 +-------------------+      \ /      .-=-.     \ /       +-------------------+
 +-------------------+    ___^______'__^__`_____v____    +-------------------+
 |                   |   |   |+Zssc    |+Zsc |       |   |                   |
 |                   |---|<--x   |  <--x     |       |---|                   |
 |                   |---|+Yssc  | +Ysc      |       |---|                   |
 |                   |   |  .---------^^-----+      _|   |                   |
 +-------------------+   +-'    .'   '|+Zmsc `.____|\    +-------------------+
 +-------------------+    ||--.'---<--x_.'-----`.-----   +-------------------+
 |                   |      .'   _.+Ymsc  `-._   `. -=   |                   |
 |                   |    .'  _.'             `_.  `.    |                   |
 |                   |  .' .-'                   `-. `.  |                   |
 |                   | ---'                         `--- |                   |
 +-------------------+                                   +-------------------+


      \begindata

         FRAME_MMX_SHV_MSC        = -239050
         FRAME_-239050_NAME       = 'MMX_SHV_MSC'
         FRAME_-239050_CLASS      = 4
         FRAME_-239050_CLASS_ID   = -239050
         FRAME_-239050_CENTER     = -239
         TKFRAME_-239050_SPEC     = 'ANGLES'
         TKFRAME_-239050_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239050_ANGLES   = (   -3.0     0.0     0.0 )
         TKFRAME_-239050_AXES     = (    2       3       1   )
         TKFRAME_-239050_UNITS    = 'DEGREES'

         FRAME_MMX_SHV_SSC        = -239051
         FRAME_-239051_NAME       = 'MMX_SHV_SSC'
         FRAME_-239051_CLASS      = 4
         FRAME_-239051_CLASS_ID   = -239051
         FRAME_-239051_CENTER     = -239
         TKFRAME_-239051_SPEC     = 'ANGLES'
         TKFRAME_-239051_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239051_ANGLES   = (  180.0     0.0     0.0 )
         TKFRAME_-239051_AXES     = (    1       2       3   )
         TKFRAME_-239051_UNITS    = 'DEGREES'

      \begintext


Sampler Frames definitions
--------------------------

In this section, the sampler frames -- MMX_C-SMP and MMX_P-SMP --
will be defined.



MMX Science Instrument Frames
---------------------------------------------------------------------------

   This section contains frame definitions for the MMX science instruments.

   The instrument frames are defined as fixed offset frames with their
   orientation specified using Euler angles.

   Note that angles in the frame definitions are specified for
   "from instrument to base (relative to) frame" transformation.


CMDM Frame definition
---------------------

   The CMDM frame -- MMX_CMDM -- is defined as follows [5,7]:

      - +X axis is nominally co-aligned with the s/c +X axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis;

      - +Z axis completes the right hand frame;

      - the origin of the frame is at the center of the polyimide film as
        the detector. [TBD]

   The CMDM instrument is mounted on the -X panel of the spacecraft with
   -X direction field of view of the spacecraft and the MMX_CMDM frame is
   shown on this diagram:

  S/C -X side view:
  -----------------

                               _               _
                              | |.-----------.| |
                              \ /|   .---.   |\ /
                              _v |   |   |   | v_
 +-------------------+       |  ||   |   |   ||  |       +-------------------+
 |                   |       |  ||   |   |   ||  |       |                   |
 |                   |       |__||   |   |   ||__|       |                   |
 |                   |       _   |   |   |   |  _        |                   |
 |                   |      | |  |   |   |   | | |       |                   |
 +-------------------+      \ /  |   `---'   | \ /       +-------------------+
 +-------------------+    ___v___|_____^_____|__v____    +-------------------+
 |                   |   |       |     |+Zsc |   ^+Zcmdm |                   |
 |                   |---|       |  <--x     |   |   |---|                   |
 |                   |---|       | +Ysc      |<--x   |---|                   |
 |                   |   |  .----------^-----+ +Ycmdm|   |                   |
 +-------------------+   +-'    .'   '   `   `.____|\    +-------------------+
 +-------------------+    ||--.'-----`._.'-----`.-----   +-------------------+
 |                   |      .'   _.-'     `-._   `. -=   |                   |
 |                   |    .'  _.'             `_.  `.    |                   |
 |                   |  .' .-'                   `-. `.  |                   |
 |                   | ---'                         `--- |                   |
 +-------------------+                                   +-------------------+


      \begindata

         FRAME_MMX_CMDM           = -239100
         FRAME_-239100_NAME       = 'MMX_CMDM'
         FRAME_-239100_CLASS      = 4
         FRAME_-239100_CLASS_ID   = -239100
         FRAME_-239100_CENTER     = -239
         TKFRAME_-239100_SPEC     = 'ANGLES'
         TKFRAME_-239100_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239100_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239100_AXES     = (    3       2       1   )
         TKFRAME_-239100_UNITS    = 'DEGREES'

      \begintext


LIDAR Frames definition
-----------------------

   The LIDAR base frame -- MMX_LIDAR_BASE -- is defined as follows [5,8]:

      - -Z axis is along the boresights of LIDAR transmitter laser and
        LIDAR receiver telescope and nominally co-aligned
        with the s/c -Z axis;

      - +X axis is nominally co-aligned with the s/c +X axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis and
        completes the right hand frame;

      - the origin of the frame is at reference hole of LIDAR at the
        mounting surface of the LIDAR to the spacecraft.


   The LIDAR transmitter frame -- MMX_LIDAR_TX -- is defined as follows [8]:

      - -Z axis is along the boresights of LIDAR transmitter laser and
        co-aligned with the LIDAR base frame -Z axis;

      - +X axis is nominally co-aligned with the LIDAR base frame +X axis;

      - +Y axis is nominally co-aligned with the LIDAR base frame +Y axis
        and completes the right hand frame;

      - the origin of the frame is at the center of the Laser Expander
        (transmitter) of the LIDAR in the X-Y plane and the mounting
        surface of the LIDAR to the spacecraft in the Z direction.


   The LIDAR receiver frame -- MMX_LIDAR_RX -- is defined as follows [8]:

      - -Z axis is along the boresights of LIDAR receiver and
        co-aligned with the LIDAR base frame -Z axis;

      - +X axis is nominally co-aligned with the LIDAR base frame +X axis;

      - +Y axis is nominally co-aligned with the LIDAR base frame +Y axis
        and completes the right hand frame;

      - the origin of the frame is at the focal point of the
        Cassagrain Telescope (receiver) of the LIDAR.


   S/C -Z side ("bottom") view with the exploration module:
   --------------------------------------------------------
        _____                                                          _____
       /     \                                                        /     \
      /       \                          __                          /       \
      \       `-._                      |  |                      _.-'       /
       \____\\``  `-._      ___________/|  |                  _.-'  ''//____/
             \\ ``    `-._  ---------------|------------  _.-'    '' //
              \\  ``      `-._         .'  `.         _.-'      ''  //
               \\   ``        `-._   .'      `.   _.-'        ''   //
                \\    ``          `.'          `.'          ''    //
   SAP          _\\     ``       .'              `.       ''     //_      SAP
   ------------|  \\      ``   .'       _____      `.   ''      //  |---------
               |   \\       ``'        |     |       `''       //   |
               |    \\      .'         |     |       __`.     //    |
               |     \\   .'           |_____|      |   |`.  //     |
               | .--. \\.'                          |___|  `//      |
               | |  |  \\                ^+Xsc             //`. __  |
               | `--'   \\    +Zsc is    |                //   |  | |
               |==             into the  x--->                 |  | |
               |_____   //     page        +Ysc           \\   |__| |
               |     `.//                                  \\.'     |
               |      //.                                  .\\      |
               |     //  `.   ^ +Xlidar                  .'  \\     |
               |    //     `.-|-.                      .'     \\    |
               |   // LIDAR | x---> +Ylidar          .'        \\   |
               |_ //       ''---                   .' ``        \\ _|
                 //      ''      `.              .'     ``       \\
                //     ''          `_.-'    `-._'         ``      \\
               //    ''         _.-' ---------- `-._        ``     \\
              //   ''       _.-'     |        |     `-._      ``    \\
         ____//  ''     _.-'         |        |         `-._    ``   \\_____
        /   //\''   _.-'             |        | ___         `-._  ``  \\    \
       /       \_.-'                _|        ||_o_|            `-._``       \
       \       /                    |_        _|                     \       /
        \_____/                       `|____.'                        \_____/



      \begindata

         FRAME_MMX_LIDAR_BASE     = -239110
         FRAME_-239110_NAME       = 'MMX_LIDAR_BASE'
         FRAME_-239110_CLASS      = 4
         FRAME_-239110_CLASS_ID   = -239110
         FRAME_-239110_CENTER     = -239
         TKFRAME_-239110_SPEC     = 'ANGLES'
         TKFRAME_-239110_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239110_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239110_AXES     = (    3       2       1   )
         TKFRAME_-239110_UNITS    = 'DEGREES'

         FRAME_MMX_LIDAR_TX       = -239111
         FRAME_-239111_NAME       = 'MMX_LIDAR_TX'
         FRAME_-239111_CLASS      = 4
         FRAME_-239111_CLASS_ID   = -239111
         FRAME_-239111_CENTER     = -239
         TKFRAME_-239111_SPEC     = 'ANGLES'
         TKFRAME_-239111_RELATIVE = 'MMX_LIDAR_BASE'
         TKFRAME_-239111_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239111_AXES     = (    3       2       1   )
         TKFRAME_-239111_UNITS    = 'DEGREES'

         FRAME_MMX_LIDAR_RX       = -239112
         FRAME_-239112_NAME       = 'MMX_LIDAR_RX'
         FRAME_-239112_CLASS      = 4
         FRAME_-239112_CLASS_ID   = -239112
         FRAME_-239112_CENTER     = -239
         TKFRAME_-239112_SPEC     = 'ANGLES'
         TKFRAME_-239112_RELATIVE = 'MMX_LIDAR_BASE'
         TKFRAME_-239112_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239112_AXES     = (    3       2       1   )
         TKFRAME_-239112_UNITS    = 'DEGREES'

      \begintext


MIRS Frame definitions
---------------------

   The MIRS frame -- MMX_MIRS  -- is defined as follows [5,9]:

      - -Z axis is nominally co-aligned with the s/c -Z axis;

      - +X axis is nominally co-aligned with the s/c +X axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis and
        completes the right hand frame;

      - the origin of the frame is at a focal point of the MIRS optics;


   The MMX MIRS scan frame -- MMX_MIRS_SCAN -- is defined as follows [9]:

      - -Z axis is along the boresight of the MIRS, moving along the
        scanning mirror, and nominally co-aligned with the s/c -Z axis
        when the scanning mirror is at the nominal 'nadir-pointing'
        direction;

      - +X axis is along the along-track direction of the s/c and nominally
        co-aligned with the s/c +X axis when the scanning mirror is at the
        nominal 'nadir-pointing' direction;

      - +Y axis completes the right hand frame;

      - the origin of the frame is same as the MMX_MIRS frame;


   S/C -Z side ("bottom") view with the exploration module:
   --------------------------------------------------------
        _____                                                          _____
       /     \                                                        /     \
      /       \                          __                          /       \
      \       `-._                      |  |                      _.-'       /
       \____\\``  `-._      ___________/|  |                  _.-'  ''//____/
             \\ ``    `-._  ---------------|------------  _.-'    '' //
              \\  ``      `-._         .'  `.         _.-'      ''  //
               \\   ``        `-._   .'      `.   _.-'        ''   //
                \\    ``          `.'          `.'          ''    //
   SAP          _\\     ``       .'              `.       ''     //_      SAP
   ------------|  \\      ``   .'       _____      `.   ''      //  |---------
               |   \\       ``'        |     |       `''       //   |
               |    \\      .'         |     |       __`.     //    |
               |     \\   .'           |_____|      |   |`.  //     |
               | .--. \\.'                          |___|  `//  ^+Xmirs
               | |  |  \\                ^+Xsc             //`. |_  |
               | `--'   \\    +Zsc is    |                //   |x---> +Ymirs
               |==             into the  x--->                 |  | |
               |_____   //     page        +Ysc           \\   |__| |+Zmirs is
               |     `.//                                  \\.'     |into the
               |      //.                                  .\\      |page
               |     //  `.                              .'  \\     |
               |    //     `.---.                      .'     \\    |
               |   //       |   |                    .'        \\   |
               |_ //       ''---                   .' ``        \\ _|
                 //      ''      `.              .'     ``       \\
                //     ''          `_.-'    `-._'         ``      \\
               //    ''         _.-' ---------- `-._        ``     \\
              //   ''       _.-'     |        |     `-._      ``    \\
         ____//  ''     _.-'         |        |         `-._    ``   \\_____
        /   //\''   _.-'             |        | ___         `-._  ``  \\    \
       /       \_.-'                _|        ||_o_|            `-._``       \
       \       /                    |_        _|                     \       /
        \_____/                       `|____.'                        \_____/


      \begindata

         FRAME_MMX_MIRS           = -239120
         FRAME_-239120_NAME       = 'MMX_MIRS'
         FRAME_-239120_CLASS      = 4
         FRAME_-239120_CLASS_ID   = -239120
         FRAME_-239120_CENTER     = -239
         TKFRAME_-239120_SPEC     = 'ANGLES'
         TKFRAME_-239120_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239120_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239120_AXES     = (    3       2       1   )
         TKFRAME_-239120_UNITS    = 'DEGREES'

      \begintext

   The MIRS scan frame is provided by a Switch Frame aligned with one of
   the different CK-based frames (MMX_MIRS_SCAN_PLAN, or MMX_MIRS_SCAN_MEAS)
   depending on coverage. MMX_MIRS_SCAN_MEAS has priority over
   MMX_MIRS_SCAN_PLAN whenever coverage for both is available.

      \begindata

         FRAME_MMX_MIRS_SCAN        = -239121
         FRAME_-239121_NAME         = 'MMX_MIRS_SCAN'
         FRAME_-239121_CLASS        = 6
         FRAME_-239121_CLASS_ID     = -239121
         FRAME_-239121_CENTER       = -239
         FRAME_-239121_ALIGNED_WITH = (
                                        'MMX_MIRS_SCAN_PLAN',
                                        'MMX_MIRS_SCAN_MEAS'
                                      )

      \begintext

   The MIRS scan planning frame -- MMX_MIRS_SCAN_PLAN -- is defined in
   order to accommodate the C-kernels that have been generated with a
   fictional SCLK kernel. These CK kernels contain predicted and test
   data and are used for planning purposes.

   The before-mentioned CKs are generated with a fictional SCLK kernel
   due to the fact that successive updates of the real SCLK kernel would
   lead to erroneous results for the predicted data provided by those
   kernels after the last Time Correlation Packet offered by the real
   SCLK.

   Since the MIRS scan frame orientation is defined with respect to MIRS
   base frame and provided by a C-kernel (see [3] for more information),
   this frame is defined as a CK-based frame. These sets of keywords
   define the MMX_MIRS_SCAN_PLAN frame.

      \begindata

         FRAME_MMX_MIRS_SCAN_PLAN  = -239122
         FRAME_-239122_NAME        = 'MMX_MIRS_SCAN_PLAN'
         FRAME_-239122_CLASS       = 3
         FRAME_-239122_CLASS_ID    = -239122
         FRAME_-239122_CENTER      = -239
         CK_-239122_SCLK           = -239999
         CK_-239122_SPK            = -239

      \begintext

   The MMX MIRS scan measured frame -- MMX_MIRS_SCAN_MEAS -- is defined
   in order to accommodate the C-kernels that have been generated with a
   real SCLK kernel. These C-kernels contain measured data from the
   housekeeping telemetry and are mainly used for data analysis.

   Since the MIRS scan frame measured orientation is defined with respect
   to the MIRS base frame and provided by a C-kernel (see [3] for more
   information), this frame is defined as a CK-based frame.

      \begindata

         FRAME_MMX_MIRS_SCAN_MEAS  = -239123
         FRAME_-239123_NAME        = 'MMX_MIRS_SCAN_MEAS'
         FRAME_-239123_CLASS       = 3
         FRAME_-239123_CLASS_ID    = -239123
         FRAME_-239123_CENTER      = -239
         CK_-239123_SCLK           = -239
         CK_-239123_SPK            = -239

      \begintext



MEGANE Frame definitions
------------------------

   The MEGANE GRS frame -- MMX_MEGANE_GRS -- is defined as follows:

      - -Z axis is nominally co-aligned with the s/c -Z axis;

      - +X axis is nominally co-aligned with the s/c +X axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is the center of the HPGe crystal.


   The MEGANE NS frame -- MMX_MEGANE_NS -- is defined as follows:

      - -Z axis is nominally co-aligned with the s/c -Z axis;

      - +X axis is nominally co-aligned with the s/c +X axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is midway between the NS sensors
        (x-axis), and midway along the length of the sensors (y-axis).


      \begindata

         FRAME_MMX_MEGANE_GRS     = -239130
         FRAME_-239130_NAME       = 'MMX_MEGANE_GRS'
         FRAME_-239130_CLASS      = 4
         FRAME_-239130_CLASS_ID   = -239130
         FRAME_-239130_CENTER     = -239
         TKFRAME_-239130_SPEC     = 'ANGLES'
         TKFRAME_-239130_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239130_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239130_AXES     = (    3       2       1   )
         TKFRAME_-239130_UNITS    = 'DEGREES'

         FRAME_MMX_MEGANE_NS      = -239140
         FRAME_-239140_NAME       = 'MMX_MEGANE_NS'
         FRAME_-239140_CLASS      = 4
         FRAME_-239140_CLASS_ID   = -239140
         FRAME_-239140_CENTER     = -239
         TKFRAME_-239140_SPEC     = 'ANGLES'
         TKFRAME_-239140_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239140_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239140_AXES     = (    3       2       1   )
         TKFRAME_-239140_UNITS    = 'DEGREES'

      \begintext


MSA Frame definitions
---------------------

   The MSA-S frame -- MMX_MSA-S -- is defined as follows [5,10]:

      - +X axis is along the boresight of the MSA-S and
        nominally co-aligned with the s/c -X axis;

      - +Y axis is nominally co-aligned with the s/c +Y axis;

      - +Z axis completes the right hand frame;

      - the origin of the frame is at the origin of the MSA FOV.


   The MSA MG-S1 frame -- MMX_MSA_MG-S1 -- is defined as follows [5,10]:

      - +X axis is rotated about 45 degrees about the s/c +Z axis;

      - +Z axis is nominally co-aligned with the s/c -Z axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is at the center of the three sensors.


   The MSA MG-S2 frame -- MMX_MSA_MG-S2 -- is defined as follows [5,10]:

      - +X axis is rotated about -45 degrees about the s/c +Z axis;

      - +Z axis is nominally co-aligned with the s/c +Z axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is at the center of the three sensors.


   S/C -Z side ("bottom") view with the exploration module:
   --------------------------------------------------------
        _____                                                          _____
       /     \             +Zmsa-s is                             /     \
      /       \            out of the    __ +Ymsa-s                  /       \
      \       `-._         page         |o--->                    _.-'       /
       \____\\``  `-._      ___________/|| |                  _.-'  ''//____/
             \\ ``    `-._  -------------V-|------------  _.-'    '' //
              \\  ``      `-._         .' +Xmsa-s     _.-'      ''  //
               \\   ``        `-._   .'      `.   _.-'        ''   //
                \\    ``          `.'          `.'          ''    //
   SAP          _\\     ``       .'              `.       ''     //_      SAP
   ------------|  \\      ``   .'       _____      `.   ''      //  |---------
               |   \\       ``'        |     |       `''       //   |
               |    \\      .'         |     |       __`.     //    |
               |     \\   .'           |_____|      |   |`.  //     |
               | .--. \\.'                          |___|  `//      |
               | |  |  \\                ^+Xsc             //`. __  |
               | `--'   \\    +Zsc is    |                //   |  | |
               |==             into the  x--->                 |  | |
               |_____   //     page        +Ysc           \\   |__| |
               |     `.//                                  \\.'     |
               |      //.                                  .\\      |
               |     //  `.                              .'  \\     |
               |    //     `.---.                      .'     \\    |
               |   //       |   | +Xmgs1  +Ymgs2     .'        \\   |
               |_ //       ''--- ._   _.   ._      .' ``        \\ _|
                 //      ''+Ymgs1'\  /`    '\    .'     ``       \\
                //     ''          `o'       `x '   +Zmgs2 is     \\
               //    ''         _.-' --------/- `-._into the page  \\
              //   ''   +Zmgs1 is    |     \/_|     `-._      ``    \\
         ____//  ''     out of the   |    +Xmgs2        `-._    ``   \\_____
        /   //\''   _.-'page         |        | ___         `-._  ``  \\    \
       /       \_.-'                _|        ||_o_|            `-._``       \
       \       /                    |_        _|                     \       /
        \_____/                       `|____.'                        \_____/


      \begindata

         FRAME_MMX_MSA-S          = -239150
         FRAME_-239150_NAME       = 'MMX_MSA-S'
         FRAME_-239150_CLASS      = 4
         FRAME_-239150_CLASS_ID   = -239150
         FRAME_-239150_CENTER     = -239
         TKFRAME_-239150_SPEC     = 'ANGLES'
         TKFRAME_-239150_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239150_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239150_AXES     = (    3       2       1   )
         TKFRAME_-239150_UNITS    = 'DEGREES'

         FRAME_MMX_MSA_MG-S1      = -239160
         FRAME_-239160_NAME       = 'MMX_MSA_MG-S1'
         FRAME_-239160_CLASS      = 4
         FRAME_-239160_CLASS_ID   = -239160
         FRAME_-239160_CENTER     = -239
         TKFRAME_-239160_SPEC     = 'ANGLES'
         TKFRAME_-239160_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239160_ANGLES   = (  -45.0     0.0     0.0 )
         TKFRAME_-239160_AXES     = (    3       2       1   )
         TKFRAME_-239160_UNITS    = 'DEGREES'

         FRAME_MMX_MSA_MG-S2      = -239170
         FRAME_-239170_NAME       = 'MMX_MSA_MG-S2'
         FRAME_-239170_CLASS      = 4
         FRAME_-239170_CLASS_ID   = -239170
         FRAME_-239170_CENTER     = -239
         TKFRAME_-239170_SPEC     = 'ANGLES'
         TKFRAME_-239170_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239170_ANGLES   = (   45.0     0.0     0.0 )
         TKFRAME_-239170_AXES     = (    3       2       1   )
         TKFRAME_-239170_UNITS    = 'DEGREES'

      \begintext


IREM Frame definitions
---------------------

   The IREM frame -- MMX_IREM -- is defined as follows [5,11]:

      - -Z axis is nominally co-aligned with the s/c -Z axis;

      - +X axis is nominally co-aligned with the s/c +X axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is at the origin of the FOV of IREM.


  S/C -X side view:
  -----------------

                               _               _
                              | |.-----------.| |
                              \ /|   .---.   |\ /
                              _v |   |   |   | v_
 +-------------------+       |  ||   |   |   ||  |       +-------------------+
 |                   |       |  ||   |   |   ||  |       |                   |
 |                   |       |__||   |   |   ||__|       |                   |
 |                   |       _   |   |   |   |  _        |                   |
 |                   |      | |  |   |   |   | | |       |                   |
 +-------------------+      \ /  |  ..---..  | \ /       +-------------------+
 +-------------------+    ___v___|_-___^___-_|__^____    +-------------------+
 |                   |   |       /     |+Zsc \  |+Zir|   |                   |
 |                   |---|      |      o-->   | o--> |---|                   |
 |                   |---|       \       +Ysc/   +Yir|---|                   |
 |                   |   |--_____ \_       _/        |   |                   |
 +-------------------+   |      .'  ``---''  `.______|    +-------------------+
 +-------------------+   +----.'------._.------`.-----   +-------------------+
 |                   |      .'   _.-'     `-._   `. -=   |                   |
 |                   |    .'  _.'             `_.  `.    |                   |
 |                   |  .' .-'                   `-. `.  |                   |
 |                   | ---'                         `--- |                   |
 +-------------------+                                   +-------------------+


      \begindata

         FRAME_MMX_IREM           = -239180
         FRAME_-239180_NAME       = 'MMX_IREM'
         FRAME_-239180_CLASS      = 4
         FRAME_-239180_CLASS_ID   = -239180
         FRAME_-239180_CENTER     = -239
         TKFRAME_-239180_SPEC     = 'ANGLES'
         TKFRAME_-239180_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239180_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239180_AXES     = (    3       2       1   )
         TKFRAME_-239180_UNITS    = 'DEGREES'

      \begintext


TENGOO Frame definitions
------------------------

   The TENGOO frame -- MMX_TENGOO -- is defined as follows [5,12,15]:

      - -Z axis is along the boresight direction of the TENGOO and
        almost co-aligned with the s/c -Z axis;
        -Z axis is tilted from the s/c -Z axis at 0.48 degree in the
        235.8 degree clockwise azimuth direction from the s/c X axis
        around the s/c -Z axis;

      - +X axis is almost co-aligned with the s/c +X axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is at the focal point of the TENGOO
        optics;

   The TENGOO instrument is on the -Z panel of the spacecraft with
   approximately -Z direction field of view of the spacecraft.


   S/C -Z side ("bottom") view with the exploration module:
   --------------------------------------------------------
        _____                                                          _____
       /     \                                                        /     \
      /       \                          __                          /       \
      \       `-._                      |  |                      _.-'       /
       \____\\``  `-._      ___________/|  |                  _.-'  ''//____/
             \\ ``    `-._  ---------------|------------  _.-'    '' //
              \\  ``      `-._         .'  `.         _.-'      ''  //
               \\   ``        `-._   .'      `.   _.-'        ''   //
                \\    ``          `.'          `.'          ''    //
   SAP          _\\     ``       .'              `.       ''     //_      SAP
   ------------|  \\      ``   .'       _____      `.   ''      //  |---------
               |   \\       ``'        |     |       `''       //   |
               |    \\     ^.+Xten     |     |       __`.     //    |
               |     \\   .|-.         |_____|      |   |`.  //     |
               | .--. \\.'|x--> +Yten               |___|  `//      |
               | |  |  \\ `--'           ^+Xsc             //`. __  |
               | `--'   \\ +Zsc and      |                //   |  | |
               |==         +Zten are     x--->                 |  | |
               |_____   // into the page   +Ysc           \\   |__| |
               |     `.//                                  \\.'     |
               |      //.                                  .\\      |
               |     //  `.                              .'  \\     |
               |    //     `.---.                      .'     \\    |
               |   //       |   |                    .'        \\   |
               |_ //       ''---                   .' ``        \\ _|
                 //      ''      `.              .'     ``       \\
                //     ''          `_.-'    `-._'         ``      \\
               //    ''         _.-' ---------- `-._        ``     \\
              //   ''       _.-'     |        |     `-._      ``    \\
         ____//  ''     _.-'         |        |         `-._    ``   \\_____
        /   //\''   _.-'             |        | ___         `-._  ``  \\    \
       /       \_.-'                _|        ||_o_|            `-._``       \
       \       /                    |_        _|                     \       /
        \_____/                       `|____.'                        \_____/



      \begindata

         FRAME_MMX_TENGOO         = -239190
         FRAME_-239190_NAME       = 'MMX_TENGOO'
         FRAME_-239190_CLASS      = 4
         FRAME_-239190_CLASS_ID   = -239190
         FRAME_-239190_CENTER     = -239
         TKFRAME_-239190_SPEC     = 'ANGLES'
         TKFRAME_-239190_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239190_ANGLES   = ( -235.8     0.48   235.8 )
         TKFRAME_-239190_AXES     = (    3       2        3   )
         TKFRAME_-239190_UNITS    = 'DEGREES'

      \begintext


OROCHI Frame definitions
------------------------

   The OROCHI base frame -- MMX_OROCHI_BASE -- is defined as follows [5,13]:

      - -Z axis is along the boresight direction of all OROCHI camera
        heads and nominally co-aligned with the s/c -Z axis;

      - +X axis is nominally co-aligned with the s/c +X axis;

      - +Y axis completes the right hand frame;

      - the origin of the frame is at the reference hole of OROCHI.

   The OROCHI camera frames -- MMX_OROCHI_390, MMX_OROCHI_480,
   MMX_OROCHI_550, MMX_OROCHI_650, MMX_OROCHI_730, MMX_OROCHI_860,
   MMX_OROCHI_950, MMX_OROCHI_VIS -- are defined as follows [13]:

      - -Z axis is along the boresight direction of each OROCHI
        camera head and nominally co-aligned with the -Z axis of the
        OROCHI base frame;

      - +X axis is nominally co-aligned with the +X axis of the OROCHI
        base frame;

      - the origin of the frame is at the focal point of the optics of
        each camera head;

   The OROCHI LED frame -- MMX_OROCHI_LED -- is defined as follows [13]:

      - -Z axis is along the boresight direction of the OROCHI LED and
        nominally co-aligned with the -Z axis of the OROCHI base frame;

      - +X axis is nominally co-aligned with the +X axis of the OROCHI
        base frame;

      - the origin of the frame is at the LED;


   S/C -Z side ("bottom") view with the exploration module:
   --------------------------------------------------------
        _____                                                          _____
       /     \                                                        /     \
      /       \                          __                          /       \
      \       `-._                      |  |                      _.-'       /
       \____\\``  `-._      ___________/|  |                  _.-'  ''//____/
             \\ ``    `-._  ---------------|------------  _.-'    '' //
              \\  ``      `-._         .'  `.         _.-'      ''  //
               \\   ``        `-._   .'      `.   _.-'        ''   //
                \\    ``          `.'          `.'          ''    //
   SAP          _\\     ``       .'              `.       ''     //_      SAP
   ------------|  \\      ``   .'       _____      `.   ''      //  |---------
               |   \\       ``'        |     |       `+Xoro    //   |
               |    \\      .'         |     |       ^_`.     //    |+Zoro is
               |     \\   .'           |_____|      ||  |`.  //     |into the
               | .--. \\.'                          |x-->  `//      |page
               | |  |  \\                ^+Xsc        +Yoro//`. __  |
               | `--'   \\    +Zsc is    |                //   |  | |
               |==             into the  x--->                 |  | |
               |_____   //     page        +Ysc           \\   |__| |
               |     `.//                                  \\.'     |
               |      //.                                  .\\      |
               |     //  `.                              .'  \\     |
               |    //     `.---.                      .'     \\    |
               |   //       |   |                    .'        \\   |
               |_ //       ''---                   .' ``        \\ _|
                 //      ''      `.              .'     ``       \\
                //     ''          `_.-'    `-._'         ``      \\
               //    ''         _.-' ---------- `-._        ``     \\
              //   ''       _.-'     |        |     `-._      ``    \\
         ____//  ''     _.-'         |        |         `-._    ``   \\_____
        /   //\''   _.-'             |        | ___         `-._  ``  \\    \
       /       \_.-'                _|        ||_o_|            `-._``       \
       \       /                    |_        _|                     \       /
        \_____/                       `|____.'                        \_____/


      \begindata

         FRAME_MMX_OROCHI_BASE    = -239200
         FRAME_-239200_NAME       = 'MMX_OROCHI_BASE'
         FRAME_-239200_CLASS      = 4
         FRAME_-239200_CLASS_ID   = -239200
         FRAME_-239200_CENTER     = -239
         TKFRAME_-239200_SPEC     = 'ANGLES'
         TKFRAME_-239200_RELATIVE = 'MMX_SPACECRAFT'
         TKFRAME_-239200_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239200_AXES     = (    3       2       1   )
         TKFRAME_-239200_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_390     = -239210
         FRAME_-239210_NAME       = 'MMX_OROCHI_390'
         FRAME_-239210_CLASS      = 4
         FRAME_-239210_CLASS_ID   = -239210
         FRAME_-239210_CENTER     = -239
         TKFRAME_-239210_SPEC     = 'ANGLES'
         TKFRAME_-239210_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239210_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239210_AXES     = (    3       2       1   )
         TKFRAME_-239210_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_480     = -239220
         FRAME_-239220_NAME       = 'MMX_OROCHI_480'
         FRAME_-239220_CLASS      = 4
         FRAME_-239220_CLASS_ID   = -239220
         FRAME_-239220_CENTER     = -239
         TKFRAME_-239220_SPEC     = 'ANGLES'
         TKFRAME_-239220_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239220_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239220_AXES     = (    3       2       1   )
         TKFRAME_-239220_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_550     = -239230
         FRAME_-239230_NAME       = 'MMX_OROCHI_550'
         FRAME_-239230_CLASS      = 4
         FRAME_-239230_CLASS_ID   = -239230
         FRAME_-239230_CENTER     = -239
         TKFRAME_-239230_SPEC     = 'ANGLES'
         TKFRAME_-239230_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239230_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239230_AXES     = (    3       2       1   )
         TKFRAME_-239230_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_650     = -239240
         FRAME_-239240_NAME       = 'MMX_OROCHI_650'
         FRAME_-239240_CLASS      = 4
         FRAME_-239240_CLASS_ID   = -239240
         FRAME_-239240_CENTER     = -239
         TKFRAME_-239240_SPEC     = 'ANGLES'
         TKFRAME_-239240_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239240_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239240_AXES     = (    3       2       1   )
         TKFRAME_-239240_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_730     = -239250
         FRAME_-239250_NAME       = 'MMX_OROCHI_730'
         FRAME_-239250_CLASS      = 4
         FRAME_-239250_CLASS_ID   = -239250
         FRAME_-239250_CENTER     = -239
         TKFRAME_-239250_SPEC     = 'ANGLES'
         TKFRAME_-239250_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239250_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239250_AXES     = (    3       2       1   )
         TKFRAME_-239250_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_860     = -239260
         FRAME_-239260_NAME       = 'MMX_OROCHI_860'
         FRAME_-239260_CLASS      = 4
         FRAME_-239260_CLASS_ID   = -239260
         FRAME_-239260_CENTER     = -239
         TKFRAME_-239260_SPEC     = 'ANGLES'
         TKFRAME_-239260_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239260_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239260_AXES     = (    3       2       1   )
         TKFRAME_-239260_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_950     = -239270
         FRAME_-239270_NAME       = 'MMX_OROCHI_950'
         FRAME_-239270_CLASS      = 4
         FRAME_-239270_CLASS_ID   = -239270
         FRAME_-239270_CENTER     = -239
         TKFRAME_-239270_SPEC     = 'ANGLES'
         TKFRAME_-239270_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239270_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239270_AXES     = (    3       2       1   )
         TKFRAME_-239270_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_VIS     = -239280
         FRAME_-239280_NAME       = 'MMX_OROCHI_VIS'
         FRAME_-239280_CLASS      = 4
         FRAME_-239280_CLASS_ID   = -239280
         FRAME_-239280_CENTER     = -239
         TKFRAME_-239280_SPEC     = 'ANGLES'
         TKFRAME_-239280_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239280_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239280_AXES     = (    3       2       1   )
         TKFRAME_-239280_UNITS    = 'DEGREES'

         FRAME_MMX_OROCHI_LED     = -239290
         FRAME_-239290_NAME       = 'MMX_OROCHI_LED'
         FRAME_-239290_CLASS      = 4
         FRAME_-239290_CLASS_ID   = -239290
         FRAME_-239290_CENTER     = -239
         TKFRAME_-239290_SPEC     = 'ANGLES'
         TKFRAME_-239290_RELATIVE = 'MMX_OROCHI_BASE'
         TKFRAME_-239290_ANGLES   = (    0.0     0.0     0.0 )
         TKFRAME_-239290_AXES     = (    3       2       1   )
         TKFRAME_-239290_UNITS    = 'DEGREES'

      \begintext


MMX NAIF ID Codes -- Definitions
---------------------------------------------------------------------------

   This section contains name to NAIF ID mappings for the MMX mission.
   Once the contents of this file are loaded into the KERNEL POOL, these
   mappings become available within SPICE, making it possible to use
   names instead of ID code in high level SPICE routine calls.

        NAME (primary)         NAIF ID
        ------------------     -------

    Spacecraft and Rover:
    ---------------------

        MMX                    -239

        MMX_SPACECRAFT         -239000

        MMX_ROVER              -239600


    Structures (solar arrays, antennas, etc.):
    ------------------------------------------

        MMX_SAP1_BASE          -239010
        MMX_SAP1               -239011
        MMX_SAP2_BASE          -239014
        MMX_SAP2               -239015
        MMX_SAP_NOMINAL        -239018

        MMX_KAXHGA             -239020
        MMX_XLGA-PX            -239021
        MMX_XLGA-PZ            -239022
        MMX_XLGA-MX            -239023
        MMX_XMGA_BASE          -239024
        MMX_XMGA               -239025

        MMX_ALT1               -239030
        MMX_ALT2               -239031

        MMX_CAM-T              -239040
        MMX_CAM-W1             -239041
        MMX_CAM-W2             -239042

        MMX_SHV_MSC            -239050
        MMX_SHV_SSC            -239051

        MMX_C-SMP_JT1_BASE     -239060
        MMX_C-SMP_JT1          -239061
        MMX_C-SMP_JT2_BASE     -239062
        MMX_C-SMP_JT2          -239063
        MMX_C-SMP_JT3_BASE     -239064
        MMX_C-SMP_JT3          -239065
        MMX_C-SMP_JT4_BASE     -239066
        MMX_C-SMP_JT4          -239067
        MMX_C-SMP_JT5_BASE     -239068
        MMX_C-SMP_JT5          -239069
        MMX_C-SMP_HCAM         -239070
        MMX_C-SMP_TMCAM        -239071
        MMX_P-SMP              -239072


    Science Instruments:
    --------------------

        MMX_CMDM               -239100

        MMX_LIDAR_BASE         -239110
        MMX_LIDAR_TX           -239111
        MMX_LIDAR_RX           -239112

        MMX_MIRS               -239120
        MMX_MIRS_SCAN          -239121

        MMX_MEGANE_GRS         -239130
        MMX_MEGANE_NS          -239140

        MMX_MSA-S              -239150
        MMX_MSA_MG-S1          -239160
        MMX_MSA_MG-S2          -239170

        MMX_IREM               -239180

        MMX_TENGOO             -239190

        MMX_OROCHI_BASE        -239200
        MMX_OROCHI_390         -239210
        MMX_OROCHI_480         -239220
        MMX_OROCHI_550         -239230
        MMX_OROCHI_650         -239240
        MMX_OROCHI_730         -239250
        MMX_OROCHI_860         -239260
        MMX_OROCHI_950         -239270
        MMX_OROCHI_VIS         -239280
        MMX_OROCHI_LED         -239290

        MMX_ROVER_NAVCAM-1     -2396xx
        MMX_ROVER_NAVCAM-2     -2396xx
        MMX_ROVER_WHEELCAM-1   -2396xx
        MMX_ROVER_WHEELCAM-2   -2396xx
        MMX_ROVER_RAX          -2396xx
        MMX_ROVER_MINIRAD      -2396xx

    Sites:
    ------

        MMX_SITE_1 .. 299      -239700 -- -239899
        MMX_LANDING_SITE_1     -239900
        MMX_LANDING_SITE_2     -239901


   The keywords below implement the MMX name-ID mappings.

      \begindata

         NAIF_BODY_NAME += ( 'MARTIAN MOONS EXPLORATION' )
         NAIF_BODY_CODE += ( -239                        )

         NAIF_BODY_NAME += ( 'MMX'                       )
         NAIF_BODY_CODE += ( -239                        )

         NAIF_BODY_NAME += ( 'MMX_SPACECRAFT'            )
         NAIF_BODY_CODE += ( -239000                     )

         NAIF_BODY_NAME += ( 'MMX_SAP1_BASE'             )
         NAIF_BODY_CODE += ( -239010                     )

         NAIF_BODY_NAME += ( 'MMX_SAP2_BASE'             )
         NAIF_BODY_CODE += ( -239014                     )

         NAIF_BODY_NAME += ( 'MMX_SAP1'                  )
         NAIF_BODY_CODE += ( -239011                     )

         NAIF_BODY_NAME += ( 'MMX_SAP2'                  )
         NAIF_BODY_CODE += ( -239015                     )

         NAIF_BODY_NAME += ( 'MMX_SAP_NOMINAL'           )
         NAIF_BODY_CODE += ( -239018                     )

         NAIF_BODY_NAME += ( 'MMX_KAXHGA'                )
         NAIF_BODY_CODE += ( -239020                     )

         NAIF_BODY_NAME += ( 'MMX_XLGA-PX'               )
         NAIF_BODY_CODE += ( -239021                     )

         NAIF_BODY_NAME += ( 'MMX_XLGA-PZ'               )
         NAIF_BODY_CODE += ( -239022                     )

         NAIF_BODY_NAME += ( 'MMX_XLGA-MX'               )
         NAIF_BODY_CODE += ( -239023                     )

         NAIF_BODY_NAME += ( 'MMX_XMGA_BASE'             )
         NAIF_BODY_CODE += ( -239024                     )

         NAIF_BODY_NAME += ( 'MMX_XMGA'                  )
         NAIF_BODY_CODE += ( -239025                     )

         NAIF_BODY_NAME += ( 'MMX_ALT1'                  )
         NAIF_BODY_CODE += ( -239030                     )

         NAIF_BODY_NAME += ( 'MMX_ALT2'                  )
         NAIF_BODY_CODE += ( -239031                     )

         NAIF_BODY_NAME += ( 'MMX_CAM-T'                 )
         NAIF_BODY_CODE += ( -239040                     )

         NAIF_BODY_NAME += ( 'MMX_CAM-W1'                )
         NAIF_BODY_CODE += ( -239041                     )

         NAIF_BODY_NAME += ( 'MMX_CAM-W2'                )
         NAIF_BODY_CODE += ( -239042                     )

         NAIF_BODY_NAME += ( 'MMX_SHV_MSC'               )
         NAIF_BODY_CODE += ( -239050                     )

         NAIF_BODY_NAME += ( 'MMX_SHV_SSC'               )
         NAIF_BODY_CODE += ( -239051                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT1_BASE'        )
         NAIF_BODY_CODE += ( -239060                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT1'             )
         NAIF_BODY_CODE += ( -239061                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT2_BASE'        )
         NAIF_BODY_CODE += ( -239062                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT2'             )
         NAIF_BODY_CODE += ( -239063                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT3_BASE'        )
         NAIF_BODY_CODE += ( -239064                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT3'             )
         NAIF_BODY_CODE += ( -239065                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT4_BASE'        )
         NAIF_BODY_CODE += ( -239066                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT4'             )
         NAIF_BODY_CODE += ( -239067                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT5_BASE'        )
         NAIF_BODY_CODE += ( -239068                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_JT5'             )
         NAIF_BODY_CODE += ( -239069                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_HCAM'            )
         NAIF_BODY_CODE += ( -239070                     )

         NAIF_BODY_NAME += ( 'MMX_C-SMP_TMCAM'           )
         NAIF_BODY_CODE += ( -239071                     )

         NAIF_BODY_NAME += ( 'MMX_P-SMP'                 )
         NAIF_BODY_CODE += ( -239072                     )

         NAIF_BODY_NAME += ( 'MMX_CMDM'                  )
         NAIF_BODY_CODE += ( -239100                     )

         NAIF_BODY_NAME += ( 'MMX_LIDAR_BASE'            )
         NAIF_BODY_CODE += ( -239110                     )

         NAIF_BODY_NAME += ( 'MMX_LIDAR_TX'              )
         NAIF_BODY_CODE += ( -239111                     )

         NAIF_BODY_NAME += ( 'MMX_LIDAR_RX'              )
         NAIF_BODY_CODE += ( -239112                     )

         NAIF_BODY_NAME += ( 'MMX_MIRS'                  )
         NAIF_BODY_CODE += ( -239120                     )

         NAIF_BODY_NAME += ( 'MMX_MIRS_SCAN'             )
         NAIF_BODY_CODE += ( -239121                     )

         NAIF_BODY_NAME += ( 'MMX_MEGANE_GRS'            )
         NAIF_BODY_CODE += ( -239130                     )

         NAIF_BODY_NAME += ( 'MMX_MEGANE_NS'             )
         NAIF_BODY_CODE += ( -239140                     )

         NAIF_BODY_NAME += ( 'MMX_MSA-S'                 )
         NAIF_BODY_CODE += ( -239150                     )

         NAIF_BODY_NAME += ( 'MMX_MSA_MG-S1'             )
         NAIF_BODY_CODE += ( -239160                     )

         NAIF_BODY_NAME += ( 'MMX_MSA_MG-S2'             )
         NAIF_BODY_CODE += ( -239170                     )

         NAIF_BODY_NAME += ( 'MMX_IREM'                  )
         NAIF_BODY_CODE += ( -239180                     )

         NAIF_BODY_NAME += ( 'MMX_TENGOO'                )
         NAIF_BODY_CODE += ( -239190                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_BASE'           )
         NAIF_BODY_CODE += ( -239200                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_390'            )
         NAIF_BODY_CODE += ( -239210                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_480'            )
         NAIF_BODY_CODE += ( -239220                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_550'            )
         NAIF_BODY_CODE += ( -239230                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_650'            )
         NAIF_BODY_CODE += ( -239240                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_730'            )
         NAIF_BODY_CODE += ( -239250                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_860'            )
         NAIF_BODY_CODE += ( -239260                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_950'            )
         NAIF_BODY_CODE += ( -239270                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_VIS'            )
         NAIF_BODY_CODE += ( -239280                     )

         NAIF_BODY_NAME += ( 'MMX_OROCHI_LED'            )
         NAIF_BODY_CODE += ( -239290                     )

         NAIF_BODY_NAME += ( 'MMX_ROVER'                 )
         NAIF_BODY_CODE += ( -239600                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_1'                )
         NAIF_BODY_CODE += ( -239700                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_2'                )
         NAIF_BODY_CODE += ( -239701                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_3'                )
         NAIF_BODY_CODE += ( -239702                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_4'                )
         NAIF_BODY_CODE += ( -239703                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_5'                )
         NAIF_BODY_CODE += ( -239704                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_6'                )
         NAIF_BODY_CODE += ( -239705                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_7'                )
         NAIF_BODY_CODE += ( -239706                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_8'                )
         NAIF_BODY_CODE += ( -239707                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_9'                )
         NAIF_BODY_CODE += ( -239708                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_10'               )
         NAIF_BODY_CODE += ( -239709                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_11'               )
         NAIF_BODY_CODE += ( -239710                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_12'               )
         NAIF_BODY_CODE += ( -239711                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_13'               )
         NAIF_BODY_CODE += ( -239712                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_14'               )
         NAIF_BODY_CODE += ( -239713                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_15'               )
         NAIF_BODY_CODE += ( -239714                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_16'               )
         NAIF_BODY_CODE += ( -239715                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_17'               )
         NAIF_BODY_CODE += ( -239716                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_18'               )
         NAIF_BODY_CODE += ( -239717                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_19'               )
         NAIF_BODY_CODE += ( -239718                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_20'               )
         NAIF_BODY_CODE += ( -239719                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_21'               )
         NAIF_BODY_CODE += ( -239720                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_22'               )
         NAIF_BODY_CODE += ( -239721                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_23'               )
         NAIF_BODY_CODE += ( -239722                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_24'               )
         NAIF_BODY_CODE += ( -239723                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_25'               )
         NAIF_BODY_CODE += ( -239724                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_26'               )
         NAIF_BODY_CODE += ( -239725                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_27'               )
         NAIF_BODY_CODE += ( -239726                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_28'               )
         NAIF_BODY_CODE += ( -239727                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_29'               )
         NAIF_BODY_CODE += ( -239728                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_30'               )
         NAIF_BODY_CODE += ( -239729                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_31'               )
         NAIF_BODY_CODE += ( -239730                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_32'               )
         NAIF_BODY_CODE += ( -239731                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_33'               )
         NAIF_BODY_CODE += ( -239732                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_34'               )
         NAIF_BODY_CODE += ( -239733                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_35'               )
         NAIF_BODY_CODE += ( -239734                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_36'               )
         NAIF_BODY_CODE += ( -239735                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_37'               )
         NAIF_BODY_CODE += ( -239736                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_38'               )
         NAIF_BODY_CODE += ( -239737                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_39'               )
         NAIF_BODY_CODE += ( -239738                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_40'               )
         NAIF_BODY_CODE += ( -239739                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_41'               )
         NAIF_BODY_CODE += ( -239740                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_42'               )
         NAIF_BODY_CODE += ( -239741                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_43'               )
         NAIF_BODY_CODE += ( -239742                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_44'               )
         NAIF_BODY_CODE += ( -239743                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_45'               )
         NAIF_BODY_CODE += ( -239744                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_46'               )
         NAIF_BODY_CODE += ( -239745                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_47'               )
         NAIF_BODY_CODE += ( -239746                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_48'               )
         NAIF_BODY_CODE += ( -239747                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_49'               )
         NAIF_BODY_CODE += ( -239748                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_50'               )
         NAIF_BODY_CODE += ( -239749                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_51'               )
         NAIF_BODY_CODE += ( -239750                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_52'               )
         NAIF_BODY_CODE += ( -239751                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_53'               )
         NAIF_BODY_CODE += ( -239752                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_54'               )
         NAIF_BODY_CODE += ( -239753                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_55'               )
         NAIF_BODY_CODE += ( -239754                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_56'               )
         NAIF_BODY_CODE += ( -239755                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_57'               )
         NAIF_BODY_CODE += ( -239756                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_58'               )
         NAIF_BODY_CODE += ( -239757                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_59'               )
         NAIF_BODY_CODE += ( -239758                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_60'               )
         NAIF_BODY_CODE += ( -239759                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_61'               )
         NAIF_BODY_CODE += ( -239760                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_62'               )
         NAIF_BODY_CODE += ( -239761                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_63'               )
         NAIF_BODY_CODE += ( -239762                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_64'               )
         NAIF_BODY_CODE += ( -239763                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_65'               )
         NAIF_BODY_CODE += ( -239764                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_66'               )
         NAIF_BODY_CODE += ( -239765                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_67'               )
         NAIF_BODY_CODE += ( -239766                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_68'               )
         NAIF_BODY_CODE += ( -239767                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_69'               )
         NAIF_BODY_CODE += ( -239768                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_70'               )
         NAIF_BODY_CODE += ( -239769                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_71'               )
         NAIF_BODY_CODE += ( -239770                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_72'               )
         NAIF_BODY_CODE += ( -239771                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_73'               )
         NAIF_BODY_CODE += ( -239772                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_74'               )
         NAIF_BODY_CODE += ( -239773                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_75'               )
         NAIF_BODY_CODE += ( -239774                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_76'               )
         NAIF_BODY_CODE += ( -239775                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_77'               )
         NAIF_BODY_CODE += ( -239776                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_78'               )
         NAIF_BODY_CODE += ( -239777                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_79'               )
         NAIF_BODY_CODE += ( -239778                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_80'               )
         NAIF_BODY_CODE += ( -239779                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_81'               )
         NAIF_BODY_CODE += ( -239780                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_82'               )
         NAIF_BODY_CODE += ( -239781                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_83'               )
         NAIF_BODY_CODE += ( -239782                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_84'               )
         NAIF_BODY_CODE += ( -239783                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_85'               )
         NAIF_BODY_CODE += ( -239784                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_86'               )
         NAIF_BODY_CODE += ( -239785                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_87'               )
         NAIF_BODY_CODE += ( -239786                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_88'               )
         NAIF_BODY_CODE += ( -239787                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_89'               )
         NAIF_BODY_CODE += ( -239788                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_90'               )
         NAIF_BODY_CODE += ( -239789                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_91'               )
         NAIF_BODY_CODE += ( -239790                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_92'               )
         NAIF_BODY_CODE += ( -239791                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_93'               )
         NAIF_BODY_CODE += ( -239792                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_94'               )
         NAIF_BODY_CODE += ( -239793                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_95'               )
         NAIF_BODY_CODE += ( -239794                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_96'               )
         NAIF_BODY_CODE += ( -239795                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_97'               )
         NAIF_BODY_CODE += ( -239796                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_98'               )
         NAIF_BODY_CODE += ( -239797                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_99'               )
         NAIF_BODY_CODE += ( -239798                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_100'              )
         NAIF_BODY_CODE += ( -239799                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_101'              )
         NAIF_BODY_CODE += ( -239800                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_102'              )
         NAIF_BODY_CODE += ( -239801                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_103'              )
         NAIF_BODY_CODE += ( -239802                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_104'              )
         NAIF_BODY_CODE += ( -239803                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_105'              )
         NAIF_BODY_CODE += ( -239804                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_106'              )
         NAIF_BODY_CODE += ( -239805                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_107'              )
         NAIF_BODY_CODE += ( -239806                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_108'              )
         NAIF_BODY_CODE += ( -239807                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_109'              )
         NAIF_BODY_CODE += ( -239808                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_110'              )
         NAIF_BODY_CODE += ( -239809                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_111'              )
         NAIF_BODY_CODE += ( -239810                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_112'              )
         NAIF_BODY_CODE += ( -239811                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_113'              )
         NAIF_BODY_CODE += ( -239812                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_114'              )
         NAIF_BODY_CODE += ( -239813                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_115'              )
         NAIF_BODY_CODE += ( -239814                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_116'              )
         NAIF_BODY_CODE += ( -239815                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_117'              )
         NAIF_BODY_CODE += ( -239816                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_118'              )
         NAIF_BODY_CODE += ( -239817                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_119'              )
         NAIF_BODY_CODE += ( -239818                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_120'              )
         NAIF_BODY_CODE += ( -239819                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_121'              )
         NAIF_BODY_CODE += ( -239820                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_122'              )
         NAIF_BODY_CODE += ( -239821                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_123'              )
         NAIF_BODY_CODE += ( -239822                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_124'              )
         NAIF_BODY_CODE += ( -239823                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_125'              )
         NAIF_BODY_CODE += ( -239824                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_126'              )
         NAIF_BODY_CODE += ( -239825                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_127'              )
         NAIF_BODY_CODE += ( -239826                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_128'              )
         NAIF_BODY_CODE += ( -239827                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_129'              )
         NAIF_BODY_CODE += ( -239828                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_130'              )
         NAIF_BODY_CODE += ( -239829                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_131'              )
         NAIF_BODY_CODE += ( -239830                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_132'              )
         NAIF_BODY_CODE += ( -239831                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_133'              )
         NAIF_BODY_CODE += ( -239832                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_134'              )
         NAIF_BODY_CODE += ( -239833                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_135'              )
         NAIF_BODY_CODE += ( -239834                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_136'              )
         NAIF_BODY_CODE += ( -239835                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_137'              )
         NAIF_BODY_CODE += ( -239836                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_138'              )
         NAIF_BODY_CODE += ( -239837                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_139'              )
         NAIF_BODY_CODE += ( -239838                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_140'              )
         NAIF_BODY_CODE += ( -239839                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_141'              )
         NAIF_BODY_CODE += ( -239840                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_142'              )
         NAIF_BODY_CODE += ( -239841                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_143'              )
         NAIF_BODY_CODE += ( -239842                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_144'              )
         NAIF_BODY_CODE += ( -239843                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_145'              )
         NAIF_BODY_CODE += ( -239844                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_146'              )
         NAIF_BODY_CODE += ( -239845                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_147'              )
         NAIF_BODY_CODE += ( -239846                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_148'              )
         NAIF_BODY_CODE += ( -239847                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_149'              )
         NAIF_BODY_CODE += ( -239848                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_150'              )
         NAIF_BODY_CODE += ( -239849                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_151'              )
         NAIF_BODY_CODE += ( -239850                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_152'              )
         NAIF_BODY_CODE += ( -239851                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_153'              )
         NAIF_BODY_CODE += ( -239852                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_154'              )
         NAIF_BODY_CODE += ( -239853                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_155'              )
         NAIF_BODY_CODE += ( -239854                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_156'              )
         NAIF_BODY_CODE += ( -239855                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_157'              )
         NAIF_BODY_CODE += ( -239856                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_158'              )
         NAIF_BODY_CODE += ( -239857                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_159'              )
         NAIF_BODY_CODE += ( -239858                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_160'              )
         NAIF_BODY_CODE += ( -239859                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_161'              )
         NAIF_BODY_CODE += ( -239860                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_162'              )
         NAIF_BODY_CODE += ( -239861                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_163'              )
         NAIF_BODY_CODE += ( -239862                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_164'              )
         NAIF_BODY_CODE += ( -239863                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_165'              )
         NAIF_BODY_CODE += ( -239864                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_166'              )
         NAIF_BODY_CODE += ( -239865                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_167'              )
         NAIF_BODY_CODE += ( -239866                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_168'              )
         NAIF_BODY_CODE += ( -239867                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_169'              )
         NAIF_BODY_CODE += ( -239868                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_170'              )
         NAIF_BODY_CODE += ( -239869                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_171'              )
         NAIF_BODY_CODE += ( -239870                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_172'              )
         NAIF_BODY_CODE += ( -239871                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_173'              )
         NAIF_BODY_CODE += ( -239872                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_174'              )
         NAIF_BODY_CODE += ( -239873                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_175'              )
         NAIF_BODY_CODE += ( -239874                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_176'              )
         NAIF_BODY_CODE += ( -239875                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_177'              )
         NAIF_BODY_CODE += ( -239876                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_178'              )
         NAIF_BODY_CODE += ( -239877                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_179'              )
         NAIF_BODY_CODE += ( -239878                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_180'              )
         NAIF_BODY_CODE += ( -239879                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_181'              )
         NAIF_BODY_CODE += ( -239880                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_182'              )
         NAIF_BODY_CODE += ( -239881                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_183'              )
         NAIF_BODY_CODE += ( -239882                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_184'              )
         NAIF_BODY_CODE += ( -239883                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_185'              )
         NAIF_BODY_CODE += ( -239884                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_186'              )
         NAIF_BODY_CODE += ( -239885                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_187'              )
         NAIF_BODY_CODE += ( -239886                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_188'              )
         NAIF_BODY_CODE += ( -239887                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_189'              )
         NAIF_BODY_CODE += ( -239888                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_190'              )
         NAIF_BODY_CODE += ( -239889                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_191'              )
         NAIF_BODY_CODE += ( -239890                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_192'              )
         NAIF_BODY_CODE += ( -239891                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_193'              )
         NAIF_BODY_CODE += ( -239892                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_194'              )
         NAIF_BODY_CODE += ( -239893                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_195'              )
         NAIF_BODY_CODE += ( -239894                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_196'              )
         NAIF_BODY_CODE += ( -239895                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_197'              )
         NAIF_BODY_CODE += ( -239896                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_198'              )
         NAIF_BODY_CODE += ( -239897                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_199'              )
         NAIF_BODY_CODE += ( -239898                     )

         NAIF_BODY_NAME += ( 'MMX_SITE_200'              )
         NAIF_BODY_CODE += ( -239899                     )

         NAIF_BODY_NAME += ( 'MMX_LANDING_SITE_1'        )
         NAIF_BODY_CODE += ( -239900                     )

         NAIF_BODY_NAME += ( 'MMX_LANDING_SITE_2'        )
         NAIF_BODY_CODE += ( -239901                     )

         NAIF_BODY_NAME += ( 'PHOBOS_MARS_P'             )
         NAIF_BODY_CODE += ( -239910                     )

         NAIF_BODY_NAME += ( 'DEIMOS_MARS_P'             )
         NAIF_BODY_CODE += ( -239911                     )

         NAIF_BODY_NAME += ( 'MMX_MARS_P'                )
         NAIF_BODY_CODE += ( -239912                     )

         NAIF_BODY_NAME += ( 'MMX_PHOBOS_P'              )
         NAIF_BODY_CODE += ( -239913                     )

         NAIF_BODY_NAME += ( 'MMX_DEIMOS_P'              )
         NAIF_BODY_CODE += ( -239914                     )

      \begintext

End of FK file.
