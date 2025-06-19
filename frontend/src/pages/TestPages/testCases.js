export const testCases = [
  {
    id: "test-type-animation",
    name: "Testing the Type Animation Feature",
    component: () => import("./TestTypeAnimation/TestTypeAnimation"),
  },
  {
    id: "test-create-new-session",
    name: "Testing the Create New Session Feature",
    component: () => import("./TestCreateNewSession/TestCreateNewSession"),
  },
  {
    id: "test-continue",
    name: "Testing the Continue Feature",
    component: () => import("./TestContinue/TestContinue"),
  },
  {
    id: "test-submit-continue",
    name: "Testing the Submit and Continue Feature",
    component: () => import("./TestSubmitContinue/TestSubmitContinue"),
  },
  {
    id: "test-submit-new-floor",
    name: "Testing the Submit and New Floor Feature",
    component: () => import("./TestSubmitNewFloor/TestSubmitNewFloor"),
  },
  {
    id: "test-submit-complete",
    name: "Testing the Submit and Complete Feature",
    component: () => import("./TestSubmitComplete/TestSubmitComplete"),
  },
  {
    id: "test-submit-fail",
    name: "Testing the Submit and Fail Feature",
    component: () => import("./TestSubmitFail/TestSubmitFail"),
  },
  {
    id: "test-loading-animation",
    name: "Testing the Loading Animation Feature",
    component: () => import("./TestLoadingAnimation/TestLoadingAnimation"),
  },
];
