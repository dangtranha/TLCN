// init-mongo.js
function waitForPrimary() {
  while (true) {
    let isMaster = rs.isMaster();
    if (isMaster.ismaster) break;
    sleep(1000); // 1 giây
  }
}

waitForPrimary();

db = db.getSiblingDB("pipeline");
db.createCollection("sales");
db.createCollection("products");

db.createUser({
  user: "debezium",
  pwd: "dbz",
  roles: [{ role: "readWrite", db: "pipeline" }]
});
