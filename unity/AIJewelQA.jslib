mergeInto(LibraryManager.library, {
  AIJewelQA_PublishState: function (jsonPtr) {
    var json = UTF8ToString(jsonPtr);
    try {
      window.__AIJEWEL_QA__ = JSON.parse(json);
    } catch (error) {
      window.__AIJEWEL_QA__ = null;
    }
  }
});
